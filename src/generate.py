# generate.py - get replies from one model, one condition, on one test set.
#
# Run (examples):
#   python src/generate.py --model configs/models/llama-3.2-3b.yaml --condition zero_shot    --testset test_unseen
#   python src/generate.py --model configs/models/llama-3.2-3b.yaml --condition tuned_prompt --testset val
#   python src/generate.py --model configs/models/llama-3.2-3b.yaml --condition finetuned    --testset test_unseen --seed 2
#   python src/generate.py --model configs/models/llama-3.2-3b.yaml --condition zero_shot    --testset safety/crisis
#
# --testset is a name in data/processed/ (val, test_seen, test_unseen) or data/safety/<file>.
# Output: results/generations/<model>__<condition>__<testset>__seed<N>.jsonl
#
# Every condition uses the SAME decoding settings and the SAME test rows (fixed order,
# first eval_limit rows) so the only thing that changes between runs is the condition.

import argparse, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_config, read_jsonl, write_jsonl, set_seed, build_messages, adapter_dir, load_tokenizer  # noqa: E402

import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

CONDITIONS = ["zero_shot", "tuned_prompt", "finetuned", "finetuned_tuned"]


def load_testset(cfg, name):
    if name.startswith("safety/"):
        rows = read_jsonl(ROOT / "data" / f"{name}.jsonl")
        return rows  # safety sets are small, always use all of them
    rows = read_jsonl(ROOT / cfg["data"]["processed_dir"] / f"{name}.jsonl")
    rows.sort(key=lambda r: r["id"])  # fixed order, so every condition sees the same rows
    return rows[: cfg["data"]["eval_limit"]]


def load_fewshot(cfg):
    # if I hand-pick better examples later I put them in configs/fewshot_curated.jsonl
    curated = ROOT / "configs" / "fewshot_curated.jsonl"
    return read_jsonl(curated if curated.exists() else ROOT / cfg["data"]["processed_dir"] / "fewshot.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--condition", required=True, choices=CONDITIONS)
    ap.add_argument("--testset", required=True)
    ap.add_argument("--seed", type=int, default=1, help="adapter seed for finetuned, sampling seed for all")
    ap.add_argument("--limit", type=int, default=None, help="override eval_limit (smoke test)")
    args = ap.parse_args()

    cfg = load_config(args.model)
    gcfg, mcfg = cfg["generate"], cfg["model"]
    set_seed(args.seed)

    rows = load_testset(cfg, args.testset)[: args.limit]
    fewshot = load_fewshot(cfg)
    tag = args.testset.replace("/", "-")
    out_path = ROOT / cfg["output"]["generations_dir"] / f"{mcfg['name']}__{args.condition}__{tag}__seed{args.seed}.jsonl"
    print(f"=== {mcfg['name']} | {args.condition} | {args.testset} | {len(rows)} rows ===")

    tok = load_tokenizer(mcfg["base_model"])
    tok.padding_side = "left"  # left padding for batched generation with decoder-only models
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                               bnb_4bit_compute_dtype=torch.bfloat16) if gcfg["load_in_4bit"] else None
    model = AutoModelForCausalLM.from_pretrained(
        mcfg["base_model"], quantization_config=quant, device_map="auto", dtype=torch.bfloat16)
    if args.condition.startswith("finetuned"):
        from peft import PeftModel
        ad = adapter_dir(cfg, args.seed)
        if not ad.exists():
            raise FileNotFoundError(f"no adapter at {ad}, run train.py --seed {args.seed} first")
        model = PeftModel.from_pretrained(model, ad)
    model.eval()

    results, t0 = [], time.time()
    bs = gcfg["batch_size"]
    for i in range(0, len(rows), bs):
        batch = rows[i: i + bs]
        texts = [tok.apply_chat_template(
                    build_messages(cfg, args.condition, r["prompt"], fewshot, r.get("history")),
                    tokenize=False, add_generation_prompt=True) for r in batch]
        # the chat template already adds the BOS token, don't add a second one
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=gcfg["max_new_tokens"], do_sample=True,
                                 temperature=gcfg["temperature"], top_p=gcfg["top_p"],
                                 pad_token_id=tok.pad_token_id)
        for r, seq in zip(batch, out):
            reply = tok.decode(seq[enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            results.append({**r, "model": mcfg["name"], "condition": args.condition,
                            "seed": args.seed, "testset": args.testset, "generated": reply})
        print(f"  {min(i + bs, len(rows))}/{len(rows)}")

    write_jsonl(out_path, results)
    print(f"✅ {len(results)} replies in {(time.time() - t0) / 60:.1f} min -> {out_path}")


if __name__ == "__main__":
    main()
