# Browser deployment investigation (deferred)

This document retains an earlier proposed export procedure. No adapter was trained, converted or deployed in Milestone 2. The commands below are unverified historical guidance and require review against pinned package versions, model licensing and the application configuration before use. They are not a release procedure that has passed testing.

The audit found an earlier assumption that a LoRA option would apply an adapter in the browser. The proposed route instead merges the adapter with its base weights and converts the result for the browser runtime. Compatibility must be verified for the installed versions; the procedure has not been demonstrated here.

## 1. Merge the adapter

```bash
python -c "from peft import AutoPeftModelForCausalLM as M; import torch; m=M.from_pretrained('adapters/llama-3.2-3b_seed1', dtype=torch.bfloat16).merge_and_unload(); m.save_pretrained('deploy/merged/llama-3.2-3b_seed1')"
```

Then copy the tokenizer files from `adapters/llama-3.2-3b_seed1/` into the merged folder.

## 2. Convert with MLC-LLM

```bash
mlc_llm convert_weight deploy/merged/llama-3.2-3b_seed1 --quantization q4f16_1 -o deploy/mlc/llama-3.2-3b_seed1
```

```bash
mlc_llm gen_config deploy/merged/llama-3.2-3b_seed1 --quantization q4f16_1 --conv-template llama-3_1 -o deploy/mlc/llama-3.2-3b_seed1
```

Use `--conv-template qwen2` for the Qwen models.

## 3. Load it in Relevia

Upload `deploy/mlc/<run>` to a Hugging Face repo, then add it to WebLLM's `appConfig.model_list` in `relevia/src/services/releviaBrain.js`, reusing the prebuilt model library (wasm) of the same base model (the `webllm_id` in `configs/models/*.yaml`). Matching the architecture alone is not a completed compatibility check. Verify the model library, configuration, tokenizer and converted weights together before loading them.

## 4. What to measure (per model × laptop)

- model load time (first visit vs. cached)
- time to first token
- tokens/second while generating
- peak GPU memory, using a documented measurement method whose scope and limitations have been verified

Record each laptop's CPU, GPU, RAM, browser version and power mode. Run each measurement 5 times and report the median.
