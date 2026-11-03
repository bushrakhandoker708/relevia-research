# Relevia research

**Does empathy fine-tuning beat a well-tuned prompt for small on-device language models, and what does it cost in safety and in-browser performance?**

This is the research side of [Relevia](../relevia), my mental health support web app. The app is also the testbed for the deployment benchmarks.

## Layout

```
configs/
  base.yaml              shared settings: held-out emotions, LoRA, decoding
  models/*.yaml          one file per model (Llama-3.2-1B/3B, Qwen2.5-1.5B/3B)
  prompts.yaml           "plain" and "tuned" system prompts
data/
  build_dataset.py       EmpatheticDialogues -> train / val / fewshot / test_seen / test_unseen
  raw/                   downloaded data (gitignored)
  processed/             built splits (gitignored, rebuild anytime)
  safety/                crisis + sycophancy test sets (evaluation only)
src/
  common.py              config loading + prompt building, shared by everything
  train.py               QLoRA fine-tune, one model x one seed
  generate.py            replies for one model x condition x test set
  evaluate.py            automatic metrics -> results/metrics/auto_metrics.csv
  make_rating_sheet.py   blinded human-rating sheets + separate answer key
notebooks/
  colab_runner.ipynb     thin wrapper that calls the scripts on a Colab GPU
  02_results_analysis.ipynb
results/                 generations, metrics, rating sheets
adapters/                trained LoRA adapters (gitignored)
deploy/                  how to get a fine-tune into the browser (MLC)
docs/                    literature notes, plan, rating guide, prompt log
archive/                 my older scripts and data, kept for reference only
```

## Quick start

```bash
pip install -r requirements.txt
```

```bash
python data/build_dataset.py
```

```bash
python src/generate.py --model configs/models/llama-3.2-3b.yaml --condition zero_shot --testset val --limit 16
```

On Colab, open `notebooks/colab_runner.ipynb`. The full order of runs is in [docs/plan.md](docs/plan.md).

## Conditions

| Condition | Model | Prompt |
|---|---|---|
| `zero_shot` | base | plain |
| `tuned_prompt` | base | tuned + 4 few-shot examples |
| `finetuned` | base + LoRA | plain |
| `finetuned_tuned` | base + LoRA | tuned + few-shot (optional) |

## Rules that keep the results honest

1. Prompt tuning only ever looks at **val**. Every version gets logged in `docs/prompt_log.md`.
2. Held-out emotions never appear in train, val or the few-shot examples (`build_dataset.py` asserts this).
3. Safety sets are never used for training.
4. Every condition gets the same test rows, in the same order, with the same decoding settings.
5. 3 seeds per fine-tuned model.
6. Rating sheets are blinded. Keep the `KEY` files away from raters (they're gitignored).
