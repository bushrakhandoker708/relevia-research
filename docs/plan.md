# Research plan and timeline

Estimates assume **part-time, ~10–15 h/week**. Roughly halve them for full-time.

| # | Phase | Weeks | Done when |
|---|---|---|---|
| 0 | Read the 5 "still to read" papers, confirm the gap | 2 | `docs/literature.md` updated, novelty claim checked |
| 1 | Write proposal, supervisor sign-off, ethics check for human raters | 2 | Proposal approved |
| 2 | Expand safety sets, curate few-shot examples, tune the prompt on val | 3 | `data/safety/` at target size, `docs/prompt_log.md` filled in |
| 3 | Baselines: zero-shot + tuned prompt, 4 models × 3 test sets | 1–2 | Generations in `results/` |
| 4 | Fine-tune: 4 models × 3 seeds, then generate | 3 | 12 adapters + generations |
| 5 | Automatic metrics + human rating round (2–3 raters) | 4 | Rating sheets returned, agreement (Krippendorff's α) computed |
| 6 | Browser benchmarks in Relevia (merge → MLC convert → 2–3 laptops) | 2–3 | Resource table |
| 7 | Statistics, figures, writing | 4 | Full draft |
| 8 | Revision + submission (+ arXiv) | 2 | Submitted |
| | **Buffer** (MLC conversion and recruiting raters are the usual delays) | 2–3 | |
| | **Total** | **~25–28 weeks (about 6 months)** | |

## Compute

- Fine-tuning a 1–3B model with QLoRA on ~28k pairs: roughly 1–3 h per run on a Colab T4/L4. 12 runs ≈ 15–35 GPU hours.
- Generation: 4 models × 4 conditions × 3 test sets (500 rows each), at about 10–30 min each.
- Colab Pro, or a few days of rented L4/A10 time, is enough. Do a smoke test (`--limit 200`) before every real run.

## Order of runs (per model)

```
python data/build_dataset.py                       # once
python src/generate.py --model M --condition zero_shot    --testset val --limit 50   # smoke test
python src/generate.py --model M --condition tuned_prompt --testset val              # tune prompt here only
python src/train.py    --model M --seed 1              # then seeds 2, 3
python src/generate.py --model M --condition {zero_shot,tuned_prompt,finetuned} --testset {test_seen,test_unseen,safety/crisis,safety/sycophancy}
python src/evaluate.py
python src/make_rating_sheet.py --model <name> --testset test_unseen --n 50
```
