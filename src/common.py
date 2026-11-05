# common.py - shared helpers so every script loads configs and builds prompts the SAME way.
# If train.py and generate.py formatted prompts differently, my comparison would be broken.

import json, os, random, sys
from pathlib import Path

import yaml

# Windows terminals are cp1252 and my ✅ prints crashed the scripts at the very end.
# Every script imports this file, so fixing it here fixes it everywhere.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent


def load_config(model_cfg_path):
    """base.yaml + one configs/models/*.yaml merged together (model file wins)."""
    with open(ROOT / "configs" / "base.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    with open(ROOT / model_cfg_path, encoding="utf-8") as f:
        cfg["model"] = yaml.safe_load(f)
    with open(ROOT / cfg["prompts_file"], encoding="utf-8") as f:
        cfg["prompts"] = yaml.safe_load(f)
    return cfg


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows):
    # A failed/interrupted write must not expose a partial JSONL file to readers.
    import tempfile
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temp_name = stream.name
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def set_seed(seed):
    import numpy as np, torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def build_messages(cfg, condition, user_text, fewshot=None, history=None):
    """Chat messages for one condition. Training uses condition='finetuned' (plain prompt).
    history = earlier turns of the same conversation (list of {role, content})."""
    use_tuned = condition in ("tuned_prompt", "finetuned_tuned")
    msgs = [{"role": "system", "content": cfg["prompts"]["tuned" if use_tuned else "plain"]}]
    if use_tuned:
        # few-shot examples go in as real past turns, models follow that better
        # than examples pasted inside the system prompt
        for ex in fewshot or []:
            msgs.append({"role": "user", "content": ex["prompt"]})
            msgs.append({"role": "assistant", "content": ex["response"]})
    msgs.extend(history or [])
    msgs.append({"role": "user", "content": user_text})
    return msgs


def adapter_dir(cfg, seed):
    return ROOT / cfg["output"]["adapters_dir"] / f"{cfg['model']['name']}_seed{seed}"


def load_tokenizer(name_or_path):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(name_or_path, use_fast=True)
    if tok.pad_token is None:
        # Llama has a reserved pad token, use it instead of eos so padding can't
        # be confused with the real end of a reply. (Qwen already has a pad token.)
        vocab = tok.get_vocab()
        tok.pad_token = "<|finetune_right_pad_id|>" if "<|finetune_right_pad_id|>" in vocab else tok.eos_token
    return tok


def chat_ids(tok, msgs, **kw):
    # newer transformers can return a dict instead of a list, handle both
    out = tok.apply_chat_template(msgs, tokenize=True, **kw)
    return list(out["input_ids"] if hasattr(out, "keys") else out)
