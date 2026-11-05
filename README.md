# Relevia research

I am investigating whether adapting a small language model improves supportive dialogue beyond a carefully developed prompt, and what either approach costs in safety and browser performance. The [Relevia application](https://github.com/bushrakhandoker708/relevia) provides the implementation context: limited device resources, sensitive conversations and the need to explain what the system can actually support.

The investigation begins with an engineering problem. Local inference alone did not prevent shared history, inconsistent expiry or misleading privacy claims. The research pipeline also reused validation conversations as prompting examples. Those issues needed correction before a comparison between models could be interpreted credibly. Milestone 2 therefore concentrates on privacy boundaries, data separation and reproducible experiment records.

This is ongoing research, with agent-assisted implementation and documentation for my review. No model-quality results, successful fine-tuning run or measured clinical benefit are claimed.

## What the current foundation establishes

The application now uses session memory by default and explicit consent for bounded local saving. In this repository, prompt development uses reserved training conversations. Previously exposed validation groups are quarantined, and all six partitions are checked at conversation level. The recorded rebuild found zero overlap across all 15 partition pairs while preserving the existing test-file hashes.

The experiment harness records the model revision, prompt and dataset versions, decoding settings, source hashes and failures. Quality and safety fields remain unrated until an assessment is performed. This separates a working evaluation pipeline from evidence that a model performs well.

## The comparison I want to make

The first proposed comparison uses the same base model with a minimal safe prompt (A) and a developed prompt (B). Prompt development uses only development data. A later adapted condition (C) must use the same inference prompt as B so that an observed difference is not automatically attributable to changing both the weights and the prompt.

The current harness supports A and B only. It rejects C because adaptation has not been integrated into this controlled runner. Existing training and generation scripts remain available for inspection, but their presence is not evidence of completed experiments or permission to begin the next milestone.

## Run the foundation checks

From this repository:

```bash
pip install -r requirements-foundation.txt
python -m unittest discover -s tests -v
```

With the required source dataset already available locally:

```bash
python data/build_dataset.py
python scripts/check_leakage.py
```

The dataset builder writes ignored local files. Review the dataset licence and provenance before acquiring or redistributing data. The tracked historical dataset under `archive/` is excluded from the active pipeline and still needs a provenance, licence and privacy review.

For the first experiment, follow [Experiment 01](docs/experiment_01_protocol.md). Its template deliberately leaves the model revision unset. Preparation requires a verified immutable revision and creates a manifest without fabricated responses; actual generation requires the additional documented gates.

## Repository structure

| Location | Role |
|---|---|
| `data/build_dataset.py`, `src/splits.py` | Build conversation-separated train, dev, few-shot, validation and test partitions |
| `scripts/check_leakage.py` | Check group overlap and frozen test hashes |
| `scripts/run_experiment.py`, `configs/experiment_01.template.json` | Prepare and record controlled A/B runs |
| `data/synthetic_dev.jsonl` | Four synthetic development fixtures for instrumentation, not a complete benchmark |
| `tests/`, `requirements-foundation.txt` | Lightweight foundation checks without training dependencies |
| `results/milestone_2/` | Recorded verification, leakage and redacted security evidence |
| `notebooks/`, `src/train.py`, `src/generate.py` | Existing investigation tooling; model executions are not established by the notebooks |
| `docs/`, `research/notes/` | Decisions, protocols, audits and literature-review status |
| `deploy/`, `archive/` | Deferred deployment guidance and historical reference material |

## Evidence and remaining work

The recorded run passed eight Python tests and the application’s 18 JavaScript tests. The application build and changed-file lint passed; legacy lint failures remain documented. No matching credential was found in the scoped history and bundle scan, which does not prove that external or unreachable historical artifacts are free of secrets.

Browser verification and the historical dataset review remain open. Milestone 2 is therefore not signed off, and Milestone 3 has not begun. Passing these foundation checks will still leave the central research question unanswered: it requires controlled model runs, reviewed safety scenarios, blinded ratings and deployment measurements.

Start with the [milestone report](docs/milestone_2_report.md), [privacy decisions](docs/privacy_design_decisions.md), [test evidence](docs/storage_test_results.md), [leakage report](docs/dataset_leakage_report.md) and [experiment protocol](docs/experiment_01_protocol.md). The [writing guide](docs/WRITING_VOICE_GUIDE.md) records how future work should preserve reasoning, limitations and authorship accurately.
