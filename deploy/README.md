# Getting a fine-tuned model into the browser (RQ3)

WebLLM **can't load a LoRA file at runtime**; my old app silently ignored the `lora` option. To run a fine-tuned model in Relevia, I have to merge the adapter into the base model and convert the result to MLC format.

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

Upload `deploy/mlc/<run>` to a Hugging Face repo, then add it to WebLLM's `appConfig.model_list` in `relevia/src/services/releviaBrain.js`, reusing the prebuilt model library (wasm) of the same base model (the `webllm_id` in `configs/models/*.yaml`). Same architecture, same wasm; only the weights change.

## 4. What to measure (per model × laptop)

- model load time (first visit vs. cached)
- time to first token
- tokens/second while generating
- peak GPU memory (from Chrome's task manager or `chrome://gpu`)

Record each laptop's CPU, GPU, RAM, browser version and power mode. Run each measurement 5 times and report the median.
