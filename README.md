# Relevia research

I am investigating whether adapting a small language model improves supportive dialogue beyond a carefully developed prompt, and what either approach costs in safety and browser performance. The [Relevia application](https://github.com/bushrakhandoker708/relevia) provides the implementation context: limited device resources, sensitive conversations and the need to explain what the system can actually support.

The investigation begins with an engineering problem. Local inference alone did not prevent shared history, inconsistent expiry or misleading privacy claims. The research pipeline also reused validation conversations as prompting examples. Those issues needed correction before a comparison between models could be interpreted credibly. Milestone 2 therefore concentrates on privacy boundaries, data separation and reproducible experiment records.

This is ongoing research, with agent-assisted implementation and documentation for my review. A small Milestone 3 prompting pilot has now run; its preliminary agent ratings do not establish a quality improvement. No successful fine-tuning run or measured clinical benefit is claimed.

## Start here

The sections below this one are milestone records in date order, so earlier sections describe earlier states of the project. For the current picture:

| Question | Where to look | State on 21 November 2026 |
|---|---|---|
| Does a developed prompt (B) change replies compared with a minimal one (A)? | [Milestone 3](#milestone-3-first-controlled-prompting-pilot), `results/experiment_01/expanded-v1/` | Ran on 60 synthetic scenarios. B hit the output limit in 1 of 60 replies against 30 of 60 for A. This is completion behaviour, not reply quality: 0 of 120 replies have independent ratings |
| Does LoRA adaptation (C) help beyond B? | [Milestone 4](#milestone-4-lora-preparation-safety-and-write-up), `results/lora/smoke-v1/` | Not tested. Only a four-step CPU smoke test of the pipeline has run |
| Can rules route urgent messages away from the model? | [Milestone 4.1 report](docs/MILESTONE_4_1_REPORT.md), [safety evidence](docs/safety_failure_taxonomy.md) | S3 caught 43 of 46 urgent synthetic cases on its first held-out run. The same agent wrote the cases and the detector, so this is development evidence, not validation |
| When may streamed text be shown to the user? | [Release protocol](docs/response_release_protocol.md), `results/release/sim-dev-v2/` | Proposed study. Policies implemented and replayed on simulated timings only; no recorded browser streams or independent labels yet |
| What does it cost in the browser? | `results/performance/browser-v1-intel/` | One run on one integrated-GPU laptop |

The [claim–evidence matrix](paper/claim_evidence_matrix.md) lists which claims the evidence does and does not support. The [manuscript](paper/manuscript.md) is a working draft, not a submitted paper. Known problems with earlier records, and how they were handled, are in the [reproducibility audit](docs/REPRODUCIBILITY_AUDIT_2026-11-21.md) and the [dataset provenance report](docs/dataset_provenance_report.md). The historical dataset in `archive/` is quarantined and excluded from every experiment; it has not had a licence or privacy review.

## What the current foundation establishes

The application now uses session memory by default and explicit consent for bounded local saving. In this repository, prompt development uses reserved training conversations. Previously exposed validation groups are quarantined, and all six partitions are checked at conversation level. The recorded rebuild found zero overlap across all 15 partition pairs while preserving the existing test-file hashes.

The experiment harness records the model revision, prompt and dataset versions, decoding settings, source hashes and failures. Quality and safety fields remain unrated until an assessment is performed. This separates a working evaluation pipeline from evidence that a model performs well.

## The comparison I want to make

The first proposed comparison uses the same base model with a minimal safe prompt (A) and a developed prompt (B). Prompt development uses only development data. A later adapted condition (C) must use the same inference prompt as B so that an observed difference is not automatically attributable to changing both the weights and the prompt.

`scripts/run_experiment.py` still supports A and B only. Condition C is handled by `scripts/generate_bc.py`, which loads B and C from one pinned model and toggles only the adapter. That script cannot read the final test set. A LoRA adapter has so far been trained only in a four-step CPU smoke test (see Milestone 4 below), which checks the pipeline and is not a result.

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

The dataset builder writes ignored local files. Review the dataset licence and provenance before acquiring or redistributing data. The historical dataset that used to sit under `archive/` is quarantined, no longer tracked and excluded from the active pipeline. It is still in early commits and still needs a provenance, licence and privacy review.

Before committing, turn on the privacy hook with `git config core.hooksPath .githooks`. It runs `scripts/privacy_scan.py --staged`, which blocks common credential formats, personal contact details, local user paths and model-weight files, and prints fingerprints rather than values. `python scripts/privacy_scan.py --tree` checks every tracked file and also runs in CI. The scanner is the same file as the application's copy, and `tests/test_privacy_scan.py` checks that the two stay identical when both repositories are checked out side by side. It reduces risk; it does not prove that nothing private remains.

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

This section records the Milestone 2 state. The recorded run passed eight Python tests and the application’s 18 JavaScript tests. The application build and changed-file lint passed; legacy lint failures remain documented. No matching credential was found in the scoped history and bundle scan, which does not prove that external or unreachable historical artifacts are free of secrets.

The browser exception has been accepted for local research, and the unresolved historical dataset is quarantined. Milestone 3 is authorised for the controlled local pilot; public-release verification remains open. Passing these foundation checks will still leave the central research question unanswered: it requires controlled model runs, reviewed safety scenarios, blinded ratings and deployment measurements.

Start with the [milestone report](docs/milestone_2_report.md), [privacy decisions](docs/privacy_design_decisions.md), [test evidence](docs/storage_test_results.md), [leakage report](docs/dataset_leakage_report.md) and [experiment protocol](docs/experiment_01_protocol.md).


## Milestone 3: first controlled prompting pilot

The historical dataset is now quarantined and excluded from experiments. A pinned Qwen2.5-1.5B-Instruct checkpoint produced 16 responses on eight held-out synthetic scenarios after two development rounds. The primary relevance difference was +0.125 with a 95% paired bootstrap interval of −0.875 to +1.125, based on explicitly unblinded agent ratings. This does not establish that the developed prompt is better. Both conditions retained an urgent-risk failure.

Read the [Milestone 3 report](docs/milestone_3_report.md), [dataset provenance](docs/dataset_provenance_report.md), [dataset card](data/experiment_01/DATASET_CARD.md), [executed dataset audit](notebooks/01_dataset_audit.ipynb) and [baseline notebook](notebooks/03_baseline_evaluation.ipynb). Independent blinded review is the next priority. Browser verification remains a public-release blocker; LoRA requires explicit approval.

## Robustness checks on the existing evidence

[Notebook 07](notebooks/07_robustness_checks.ipynb) re-analyses saved results without running a model. After the two pairs that overlap Modern Standby are removed, the expanded-v1 latency difference shrinks from −18.9 s to a median of about −3.4 s, and the median's interval includes zero. B's replies are shorter, but B costs about 2.4 s more before the first token and more time per token. The host's decode rate also halved part-way through the run. A perturbation probe found that S1 misses "I wanna die" and loses most of its recall under ordinary typos. Figures are in `results/analysis/robustness-v1/figures/` and `results/safety/perturbation-v1/`.

## S2 safety routing

The application now runs S2, which applies the S1 rules after normalising shorthand, typos, stretched letters, leetspeak and invisible characters. On a new held-out set frozen before S2 was written, S2 detects 18 of 24 urgent cases compared with 9 for S1, with no false positives on 18 ordinary messages. The remaining misses are gaps in the underlying rules, such as "killing myself" and indirect statements. See [notebook 08](notebooks/08_s2_routing.ipynb) and `results/safety/s2-v1/`.

## Milestone 4: LoRA preparation, safety and write-up

Milestone 3 is closed as exploratory groundwork ([closure audit](docs/MILESTONE_3_CLOSURE.md)). Milestone 4 so far adds:

- `scripts/lora_pilot.py`, the controlled LoRA trainer. It uses the pre-registered settings from `configs/milestone_4.pilot.json`, selects whole conversation groups, computes loss on assistant tokens only and records a manifest. A `--pilot` run requires `--approved-by`. The smoke test ran four CPU steps and validation loss went from 4.02 to 3.67. That is a pipeline check, not evidence of learning. See [notebook 04](notebooks/04_lora_training.ipynb) and `results/lora/smoke-v1/`.
- `scripts/generate_bc.py`, which generates under B and C with lexical safety flags. These flags are pattern matches, not ratings.
- A generative safety probe and failure taxonomy that separates router misses from harmful generated text ([safety taxonomy](docs/safety_failure_taxonomy.md)).
- Browser benchmark instrumentation in the application, documented in the [benchmark protocol](docs/browser_benchmark_protocol.md). It had not been run at this stage; the first run is recorded under Milestone 4.1.
- A manuscript draft with a claim–evidence matrix in `paper/`, and an [Edinburgh brief](docs/EDINBURGH_RESEARCH_BRIEF.md).

Still missing at this stage: independent ratings (0 of 120), the approved pilot on a GPU, a browser benchmark run (one run on a single laptop followed in Milestone 4.1) and a safety set written by someone other than the detector's author.

## Milestone 4.1: urgent safety fixes and audits

S2 missed every emergency in a new frozen set (`data/safety_v4`). S3 adds an emergency tier with a fixed, non-generative response. On its single held-out run it caught 43 of 46 urgent cases (0.93, 95% interval 0.82–0.98) with no false alarms on 25 ordinary messages. On 2,873 unseen human-written EmpatheticDialogues prompts it made one false alarm. The same agent wrote the cases and the detector, so these results are not independent. The reply guard was audited on 218 real replies, all references were checked, and the first real browser benchmark ran on this laptop's integrated GPU. See the [Milestone 4.1 report](docs/MILESTONE_4_1_REPORT.md) and the [safety evidence package](docs/safety_failure_taxonomy.md).

