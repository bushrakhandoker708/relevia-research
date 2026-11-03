# train.py - QLoRA empathy fine-tune for ONE model and ONE seed.
#
# Run:
#   python src/train.py --model configs/models/llama-3.2-3b.yaml --seed 1
#   python src/train.py --model configs/models/llama-3.2-3b.yaml --seed 1 --limit 200   # quick smoke test
#
# Output: adapters/<model>_seed<N>/  (adapter + tokenizer + train_log.json)
#
# Carried over from my v2 fixes (archive/v2_llama8b_scripts/train_lora.py):
#   - 4-bit base + bf16 compute, no fp16 crash
#   - loss ONLY on the assistant reply, including its end-of-turn token, so it learns to stop
#   - padding masked through attention_mask, not by token id
#   - same chat template + system prompt as generate.py (both come from common.py)
# New:
#   - everything comes from configs, nothing hardcoded
#   - seed is an argument so I can run 3 seeds per model
#   - early-turn history is included so later replies make sense

import argparse, json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_config, read_jsonl, set_seed, build_messages, adapter_dir, load_tokenizer, chat_ids  # noqa: E402

import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="configs/models/<name>.yaml")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None, help="only use N training rows (smoke test)")
    args = ap.parse_args()

    cfg = load_config(args.model)
    tcfg, mcfg = cfg["train"], cfg["model"]
    set_seed(args.seed)
    out_dir = adapter_dir(cfg, args.seed)
    print(f"=== training {mcfg['name']} seed {args.seed} -> {out_dir} ===")

    # ---- tokenizer + 4-bit base ----
    tok = load_tokenizer(mcfg["base_model"])
    tok.padding_side = "right"
    quant = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    ) if tcfg["load_in_4bit"] else None
    model = AutoModelForCausalLM.from_pretrained(
        mcfg["base_model"], quantization_config=quant, device_map="auto", dtype=torch.bfloat16)
    model.config.use_cache = False  # cache + gradient checkpointing don't mix
    if quant:
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

    model = get_peft_model(model, LoraConfig(
        r=tcfg["lora_r"], lora_alpha=tcfg["lora_alpha"], lora_dropout=tcfg["lora_dropout"],
        target_modules=mcfg["lora_targets"], bias="none", task_type=TaskType.CAUSAL_LM))
    model.print_trainable_parameters()

    # ---- data ----
    proc = ROOT / cfg["data"]["processed_dir"]
    train_rows = read_jsonl(proc / "train.jsonl")[: args.limit]
    val_rows = read_jsonl(proc / "val.jsonl")[: 300]   # small eval set, just to watch for overfitting

    def tokenize(r):
        msgs = build_messages(cfg, "finetuned", r["prompt"], history=r["history"])
        prompt_ids = chat_ids(tok, msgs, add_generation_prompt=True)
        full_ids = chat_ids(tok, msgs + [{"role": "assistant", "content": r["response"]}])
        if full_ids[: len(prompt_ids)] != prompt_ids:
            # if this ever fires, the template adds something between turns and my
            # label mask would be in the wrong place - better to crash than train on junk
            raise ValueError("chat template prefix mismatch, label masking would be wrong")
        full_ids = full_ids[: tcfg["max_len"]]
        labels = [-100] * min(len(prompt_ids), len(full_ids)) + full_ids[len(prompt_ids):]
        return {"input_ids": full_ids, "attention_mask": [1] * len(full_ids), "labels": labels}

    def prep(rows):
        ds = Dataset.from_list([tokenize(r) for r in rows])
        # drop rows where the reply got cut off completely by max_len
        return ds.filter(lambda x: any(l != -100 for l in x["labels"]))

    train_ds, val_ds = prep(train_rows), prep(val_rows)
    print(f"train rows: {len(train_ds)}  val rows: {len(val_ds)}")

    def collate(batch):
        n = max(len(x["input_ids"]) for x in batch)
        pad = lambda seq, v: seq + [v] * (n - len(seq))
        return {
            "input_ids": torch.tensor([pad(x["input_ids"], tok.pad_token_id) for x in batch]),
            "attention_mask": torch.tensor([pad(x["attention_mask"], 0) for x in batch]),
            "labels": torch.tensor([pad(x["labels"], -100) for x in batch]),
        }

    # ---- train ----
    trainer = Trainer(
        model=model,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=collate,
        args=TrainingArguments(
            output_dir=str(out_dir / "checkpoints"),
            per_device_train_batch_size=tcfg["batch_size"],
            per_device_eval_batch_size=tcfg["batch_size"],
            gradient_accumulation_steps=tcfg["grad_accum"],
            num_train_epochs=tcfg["epochs"],
            learning_rate=tcfg["lr"],
            lr_scheduler_type="cosine",
            warmup_ratio=tcfg["warmup_ratio"],
            bf16=True,
            gradient_checkpointing=True,
            logging_steps=25,
            eval_strategy="steps",
            eval_steps=tcfg["eval_steps"],
            save_strategy="steps",
            save_steps=tcfg["eval_steps"],
            save_total_limit=1,
            report_to="none",
            remove_unused_columns=False,
            group_by_length=True,
            seed=args.seed,
        ),
    )
    t0 = time.time()
    trainer.train()
    minutes = (time.time() - t0) / 60

    model.save_pretrained(out_dir)
    tok.save_pretrained(out_dir)
    # log everything I need for the paper's training-details table
    log = {
        "model": mcfg["name"], "base_model": mcfg["base_model"], "seed": args.seed,
        "train_rows": len(train_ds), "minutes": round(minutes, 1),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "train_cfg": tcfg, "history": trainer.state.log_history,
    }
    with open(out_dir / "train_log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    print(f"🎉 done in {minutes:.1f} min -> {out_dir}")


if __name__ == "__main__":
    main()
