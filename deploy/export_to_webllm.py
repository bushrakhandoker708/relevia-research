# export_to_webllm.py - turn my trained adapter into a model the Relevia app can load.
#
# Run on Colab (Linux + GPU). MLC-LLM has no Windows wheels for this step.
#   pip install --pre -U -f https://mlc.ai/wheels mlc-llm-nightly-cu123 mlc-ai-nightly-cu123
#   python deploy/export_to_webllm.py --model configs/models/llama-3.2-3b.yaml --seed 1 \
#          --hf-repo <my-hf-username>/Relevia-3B-ft-q4f16_1-MLC
#
# Steps:
#   1. merge the LoRA adapter into the full base model (WebLLM can't load adapters)
#   2. convert + quantize to q4f16_1 with MLC-LLM
#   3. copy the runtime settings from the OFFICIAL prebuilt WebLLM model, so my weights
#      can reuse its compiled GPU code (model_lib). If these don't match, the app
#      crashes when it loads the model.
#   4. (optional) upload to Hugging Face
#   5. print the CUSTOM_MODEL object to paste into relevia/src/services/modelConfig.js

import argparse, json, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from common import ROOT, load_config, adapter_dir  # noqa: E402

QUANT = "q4f16_1"


def run(cmd):
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--hf-repo", default=None, help="e.g. myname/Relevia-3B-ft-q4f16_1-MLC (skip to only build locally)")
    args = ap.parse_args()

    cfg = load_config(args.model)
    mcfg = cfg["model"]
    ad = adapter_dir(cfg, args.seed)
    if not ad.exists():
        sys.exit(f"no adapter at {ad}, train it first")

    size = mcfg["name"].split("-")[-1].upper()           # "3B"
    model_id = f"Relevia-{size}-ft-{QUANT}-MLC"
    merged = ROOT / "deploy" / "merged" / f"{mcfg['name']}_seed{args.seed}"
    out = ROOT / "deploy" / "mlc" / model_id

    # ---- 1. merge ----
    import torch
    from peft import AutoPeftModelForCausalLM
    from transformers import AutoTokenizer
    print("Merging adapter into base model...")
    # merge in bf16 (not 4-bit) - merging into quantized weights loses quality
    model = AutoPeftModelForCausalLM.from_pretrained(ad, dtype=torch.bfloat16, device_map="cpu")
    model = model.merge_and_unload()
    model.save_pretrained(merged, safe_serialization=True)
    AutoTokenizer.from_pretrained(ad).save_pretrained(merged)
    del model

    # ---- 2. convert weights ----
    run(["mlc_llm", "convert_weight", str(merged), "--quantization", QUANT, "-o", str(out)])

    # ---- 3. config matching the official prebuilt model ----
    from huggingface_hub import hf_hub_download
    base_cfg = json.load(open(hf_hub_download(f"mlc-ai/{mcfg['webllm_id']}", "mlc-chat-config.json"), encoding="utf-8"))
    run(["mlc_llm", "gen_config", str(merged), "--quantization", QUANT,
         "--conv-template", mcfg["mlc_conv_template"],
         "--context-window-size", str(base_cfg["context_window_size"]),
         "--prefill-chunk-size", str(base_cfg["prefill_chunk_size"]),
         "-o", str(out)])

    # quick check that my config really matches the base one where it matters
    mine = json.load(open(out / "mlc-chat-config.json", encoding="utf-8"))
    for k in ["context_window_size", "prefill_chunk_size", "quantization", "vocab_size"]:
        if mine.get(k) != base_cfg.get(k):
            print(f"⚠️  {k}: mine={mine.get(k)} base={base_cfg.get(k)} - the app may fail to load this")

    # ---- 4. upload ----
    url = f"https://huggingface.co/{args.hf_repo}" if args.hf_repo else "<upload deploy/mlc/" + model_id + " and put its URL here>"
    if args.hf_repo:
        from huggingface_hub import create_repo, upload_folder
        create_repo(args.hf_repo, exist_ok=True)
        upload_folder(repo_id=args.hf_repo, folder_path=str(out))
        print(f"Uploaded -> {url}")

    shutil.rmtree(merged, ignore_errors=True)  # merged fp16 copy is big and not needed anymore

    # ---- 5. what to paste into the app ----
    tier = "lite" if size == "1B" else "standard"
    print("\n✅ Done. Paste this into relevia/src/services/modelConfig.js:\n")
    print("export const CUSTOM_MODEL = {")
    print(f"  tier: '{tier}',")
    print(f"  model_id: '{model_id}',")
    print(f"  model: '{url}',")
    print(f"  base: '{mcfg['webllm_id']}',")
    print("};")


if __name__ == "__main__":
    main()
