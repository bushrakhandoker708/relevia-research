# Archive (don't use for the paper)

Kept only so I can see how the project evolved. Nothing in here produces results for the paper.

| Folder | What | Why it's archived |
|---|---|---|
| `v1_original/empathy_42k.jsonl` | My first dataset (15k rows) | Prompts paired with random replies, `_comma_` never decoded, two of the three sources didn't exist |
| `v1_original/instruction.txt` | AI-generated instructions I followed | Lists datasets and a HF repo that don't exist. **Don't cite anything from it** |
| `v1_original/relevia files/Chatbot.jsx` | Older copy of the chat widget | The real one is `relevia/src/components/Chatbot.jsx` |
| `v2_llama8b_scripts/` | The fixed dataset + Llama-3.1-8B training scripts | Replaced by `data/build_dataset.py` and `src/train.py` (official splits, held-out emotions, configs, small models) |
| `old_adapter/` | The 168 MB Llama-8B LoRA that used to sit in the app's `public/weights/` | Trained on the broken v1 data, and the app could never load it. Gitignored |
