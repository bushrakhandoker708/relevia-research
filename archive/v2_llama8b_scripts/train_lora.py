# train_lora.py - Relevia empathy LoRA (v2)
#
# What was wrong with my DialoGPT version, so I don't do it again:
#   1. WRONG BASE MODEL. I trained on microsoft/DialoGPT-medium (GPT-2 layers:
#      c_attn/c_fc) but the website runs Llama-3.1-8B-Instruct. A LoRA only works on
#      the exact model it was trained on, so that adapter could never be used.
#   2. Loaded the model in float16 AND set fp16=True. Trainer can't unscale fp16
#      gradients, so training crashes with "Attempting to unscale FP16 gradients".
#      Now: 4-bit base + bf16 compute (QLoRA), LoRA weights stay fp32.
#   3. pad_token = eos_token and then I masked every pad_token_id with -100. That
#      also masked the real <|endoftext|> after each reply, so the model never
#      learned when to STOP talking. Now I mask only actual padding (attention_mask).
#   4. Loss was computed on the user's message too, so half the training was the
#      model learning to imitate the person who is struggling. Now only the
#      assistant reply counts for the loss.
#   5. No system prompt / chat template, so the format at training time didn't
#      match the format the app sends at inference time. Now I use the same
#      Llama-3 chat template and (almost) the same system prompt as releviaBrain.js.
#
# Run:
#   pip install -U torch transformers datasets peft bitsandbytes accelerate safetensors
#   huggingface-cli login          # needs access to meta-llama on HF
#   python dataset.py              # rebuild empathy_42k.jsonl with the fixed script first!
#   python train_lora.py
#
# Needs a GPU with ~16 GB VRAM for 8B (Colab T4 is too small for 8B at 1024 tokens,
# use an L4/A10/A100, or switch BASE to Llama-3.2-3B-Instruct to test cheaply).

import os, json, torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
from datasets import load_dataset

print("=== RELEVIA LORA TRAINING v2 - Llama-3.1-8B-Instruct ===")

# ---- 1. base model: MUST be the same model the website loads ----
BASE = "meta-llama/Llama-3.1-8B-Instruct"
DATA_FILE = "empathy_42k.jsonl"
OUT_DIR = "./relevia_lora_out"
MAX_LEN = 1024   # ED replies are short, 1024 is plenty and saves a lot of memory

# keep this close to buildPrompt() in relevia/src/services/releviaBrain.js
SYSTEM_PROMPT = (
    "You are Relevia, a 26-year-old empathetic friend who has lived through anxiety and grief. "
    "Reply in 2-4 warm, genuine sentences, validate first, offer at most one small grounding idea, "
    "never give medical advice, and encourage professional help for serious issues."
)

# ---- 2. tokenizer ----
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE, use_fast=True)
# Llama-3 has no pad token. I use a reserved token instead of eos so padding
# can never be confused with the real end-of-turn token.
if tokenizer.pad_token is None:
    tokenizer.pad_token = "<|finetune_right_pad_id|>"
tokenizer.padding_side = "right"

# ---- 3. 4-bit base (QLoRA) ----
print("Loading model in 4-bit...")
bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
model = AutoModelForCausalLM.from_pretrained(
    BASE,
    quantization_config=bnb,
    device_map="auto",
    dtype=torch.bfloat16,
)
model.config.use_cache = False   # cache + gradient checkpointing don't mix
model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

# ---- 4. LoRA on all Llama projection layers ----
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(model, lora_config)
# heads up: r=16 on all 7 modules of an 8B model is ~42M params = ~84 MB in fp16,
# NOT 3.2 MB. The "3.2 MB" name was never true. If I want it tiny I can go r=4
# on q_proj/v_proj only, but quality drops.
model.print_trainable_parameters()

# ---- 5. dataset ----
if not os.path.exists(DATA_FILE):
    # I used to silently create 2000 copies of two fake rows here and train on that.
    # Never again - fail loudly instead.
    raise FileNotFoundError(f"{DATA_FILE} not found, run `python dataset.py` first")

data = load_dataset("json", data_files=DATA_FILE, split="train")
print(f"Dataset size: {len(data)}")

# ---- 6. tokenize with the chat template + mask everything except the reply ----
def chat_ids(msgs, **kw):
    # newer transformers can hand back a dict instead of a plain list, handle both
    out = tokenizer.apply_chat_template(msgs, tokenize=True, **kw)
    return list(out["input_ids"] if isinstance(out, dict) or hasattr(out, "keys") else out)

def tokenize(sample):
    prompt_msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": sample["prompt"]},
    ]
    # prompt part = system + user + "<|start_header_id|>assistant<|end_header_id|>"
    prompt_ids = chat_ids(prompt_msgs, add_generation_prompt=True)
    full_ids = chat_ids(prompt_msgs + [{"role": "assistant", "content": sample["response"]}])
    full_ids = full_ids[:MAX_LEN]
    labels = list(full_ids)
    # loss only on the assistant reply (incl. its <|eot_id|> so it learns to stop)
    n_prompt = min(len(prompt_ids), len(labels))
    labels[:n_prompt] = [-100] * n_prompt
    return {"input_ids": full_ids, "attention_mask": [1] * len(full_ids), "labels": labels}

data = data.map(tokenize, remove_columns=data.column_names)
# drop rows where the reply got cut off completely by MAX_LEN
data = data.filter(lambda x: any(l != -100 for l in x["labels"]))
print(f"Tokenized rows: {len(data)}")

# ---- 7. collator: pad per batch, padding is ignored in the loss ----
def data_collator(batch):
    max_len = max(len(x["input_ids"]) for x in batch)
    out = {"input_ids": [], "attention_mask": [], "labels": []}
    for x in batch:
        pad = max_len - len(x["input_ids"])
        out["input_ids"].append(x["input_ids"] + [tokenizer.pad_token_id] * pad)
        out["attention_mask"].append(x["attention_mask"] + [0] * pad)
        out["labels"].append(x["labels"] + [-100] * pad)
    return {k: torch.tensor(v) for k, v in out.items()}

# ---- 8. train ----
split = data.train_test_split(test_size=0.02, seed=42)   # small eval set so I can see if it's overfitting
trainer = Trainer(
    model=model,
    train_dataset=split["train"],
    eval_dataset=split["test"],
    args=TrainingArguments(
        output_dir=OUT_DIR,
        overwrite_output_dir=True,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_train_epochs=1,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        bf16=True,
        fp16=False,
        gradient_checkpointing=True,
        logging_steps=25,
        eval_strategy="steps",
        eval_steps=250,
        save_strategy="steps",
        save_steps=500,
        save_total_limit=2,
        report_to="none",          # report_to=None means "all" in older versions, not "none"
        remove_unused_columns=False,
        group_by_length=True,      # less padding = faster
    ),
    data_collator=data_collator,
)

print("🚀 Starting training...")
trainer.train()

print("💾 Saving adapter...")
model.save_pretrained(OUT_DIR)        # writes adapter_model.safetensors directly, no .bin conversion needed
tokenizer.save_pretrained(OUT_DIR)

# ---- 9. quick sanity check before I ship anything ----
model.eval()
model.config.use_cache = True
test = [{"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "I failed my exam and I feel like a total disappointment."}]
ids = tokenizer.apply_chat_template(test, add_generation_prompt=True, return_tensors="pt").to(model.device)
with torch.no_grad():
    gen = model.generate(ids, max_new_tokens=120, do_sample=True, temperature=0.7, top_p=0.9)
print("\nSample reply:\n", tokenizer.decode(gen[0][ids.shape[1]:], skip_special_tokens=True))

# ---- 10. how this gets into the website ----
# WebLLM (@mlc-ai/web-llm) CANNOT load a LoRA file at runtime. There is no `lora`
# option, it was silently ignored. To use this fine-tune in the browser I have to:
#   a) merge the adapter into the base weights:
#        python -c "from peft import AutoPeftModelForCausalLM as M; import torch; \
#          m=M.from_pretrained('./relevia_lora_out', dtype=torch.bfloat16).merge_and_unload(); \
#          m.save_pretrained('./relevia-merged'); \
#          from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('./relevia_lora_out').save_pretrained('./relevia-merged')"
#   b) convert it with MLC-LLM:
#        mlc_llm convert_weight ./relevia-merged --quantization q4f16_1 -o ./relevia-MLC
#        mlc_llm gen_config ./relevia-merged --quantization q4f16_1 --conv-template llama-3_1 -o ./relevia-MLC
#   c) upload ./relevia-MLC to a HF repo and register it as a custom model in
#      releviaBrain.js (appConfig.model_list), reusing the prebuilt Llama-3.1-8B wasm lib.
print("\n🎉 Training complete! Adapter is in", OUT_DIR)
print("See step 10 at the bottom of this file for getting it into the website.")
