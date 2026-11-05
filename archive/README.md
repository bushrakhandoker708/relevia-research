# Historical development archive

This archive preserves the earlier development history and its known failures. It is excluded from the current evaluation pipeline and must not supply experimental results. The descriptions below reflect the existing archive account, not a new reproduction of its training or dataset construction.

The tracked `v1_original/empathy_42k.jsonl` still needs a provenance, licence and privacy review before redistribution can be endorsed. Its filename does not establish the dataset size or source. Keeping a historical artifact for inspection is not evidence that it is suitable for training or public release.

| Folder | What | Why it's archived |
|---|---|---|
| `v1_original/empathy_42k.jsonl` | Earlier dataset (reported as 15k rows) | Prompts paired with random replies, `_comma_` never decoded, two of the three sources didn't exist |
| `v1_original/instruction.txt` | Earlier AI-generated instructions | Lists datasets and a HF repo that don't exist. **Don't cite anything from it** |
| `v1_original/relevia files/Chatbot.jsx` | Older copy of the chat widget | The real one is `relevia/src/components/Chatbot.jsx` |
| `v2_llama8b_scripts/` | Earlier dataset revision and Llama-3.1-8B scripts | Replaced by `data/build_dataset.py` and `src/train.py` (official splits, held-out emotions, configs, small models) |
| `old_adapter/` | The 168 MB Llama-8B LoRA that used to sit in the app's `public/weights/` | Trained on the broken v1 data, and the app could never load it. Gitignored |
