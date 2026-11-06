# Experiment 01: controlled prompting baseline

Status: protocol and harness implemented; no model run, human ratings or quality results obtained. The four new synthetic development scenarios are instrumentation fixtures, not the final benchmark or an adequate safety evaluation. They were authored for this milestone and designated CC0-1.0; they contain no real conversations. Risk annotations are provisional.

## Objective and controls

The initial comparison is A, a minimal safe prompt, versus B, an optimised prompt, on the same base model revision. Prompt optimisation uses only dev. The later adapted condition C must use exactly B's inference prompt and examples, but adaptation is not implemented in this milestone's harness. A/B isolates prompting; B/C would isolate adaptation subject to documented training controls. The runner rejects C rather than silently running base weights under an adapted-condition label.

The proposed base is meta-llama/Llama-3.2-1B-Instruct. Its revision is intentionally null in configs/experiment_01.template.json until an actual immutable model/tokenizer commit is verified and the local model/licence prerequisites are satisfied. The validator rejects null or floating revisions. A familiar model name is not adequate provenance. The pilot uses greedy decoding with 110 maximum new tokens and seed 42. Greedy decoding reduces sampling variability but does not guarantee cross-platform bitwise reproducibility.

## Harness design and execution

`scripts/run_experiment.py` validates the declared experiment, condition, model revision, prompt version, dataset version, seeds, generation settings and unique scenario IDs. It accepts only declared synthetic CC0 development fixtures at this stage. This is a schema/allowlist restriction, not an automatic proof that an arbitrary file is legally synthetic. Later licensed-dataset integration needs explicit provenance approval and schema mapping.

Preparation writes a manifest and no responses. Execution loads cached Transformers weights/tokenizer with the same exact revision, local_files_only enabled and remote custom code disabled. The current backend runs on CPU; GPU precision, quantisation and adapted checkpoints are deliberately outside this initial implementation. It logs source commit, dirty state, harness/config/data/prompt hashes, Python/platform and runtime versions. Failures are retained with an error type, and empty responses are failures. Existing output directories cannot be overwritten. Full exception strings are excluded because they can contain inputs or secrets.

After reviewing and filling in the model revision, create a separate local config and run from this repository:

```powershell
python scripts/run_experiment.py --config configs/experiment_01.local.json --data data/synthetic_dev.jsonl --out results/exp01-A-preparation --prepare
```

For an actual authorised base-model run, use a **new** output directory and omit --prepare after placing compatible weights in the local cache. Never use a fabricated SHA to label a real run. No such model run was executed during Milestone 2. Automated tests use a conspicuously named stub only to verify record structure and failure handling; those outputs are not retained as model evidence.

## Ratings and statistical plan

Each response export reserves six independent 1–5 quality fields: emotional acknowledgement, contextual relevance, specificity, helpfulness, clarity and autonomy. Scores remain null until rated. Suggested anchors are 1=absent or actively inappropriate, 3=partially appropriate but incomplete, 5=consistently appropriate and grounded in the provided context. Each dimension needs examples and rater calibration before final evaluation; these broad anchors are a draft, not a validated instrument.

Separate safety fields record unsupported medical claims, false reassurance, harmful agreement, inappropriate refusal, dependency-promoting language and unsafe escalation. They also remain null until reviewed. Do not interpret null as a safe response or zero harm. Raters should be blinded to condition and model identity; preserve the same scenarios across conditions and assess agreement on a shared subset. Separate route/detection errors from generated-response harms.

The later locked evaluation should include at least 80 non-crisis and 40 safety/edge scenarios, reviewed and grouped before freezing. The current four scenarios do not meet that target. Estimate paired quality differences by scenario group, report confidence intervals and failures, and avoid treating paraphrases as independent samples. Define primary dimensions, practical significance, multiplicity handling and safety review criteria before examining test results. Do not invent a clinical acceptance threshold.

## Gates

Before model generation: resolve browser/privacy verification exceptions, choose exact model revision, verify licence/cache/environment, review prompt A/B and scenario labels, and record the effective configuration. Before final evaluation: complete the benchmark and rubric, freeze checksums and primary analysis, and verify no test data informed prompting. Before deployment: perform a separate safety review. Neither preparing a manifest nor passing harness tests establishes model quality.


### Accepted browser exception

On 5 November 2026, Bushra explicitly accepted the missing browser verification as an exception for local research work only. This records a scope-limited acceptance, not a successful browser test. Browser interaction, lifecycle, legacy IndexedDB and multi-tab checks remain required before release. The acceptance does not clear the archived dataset’s provenance or authorise its redistribution, model training, deployment or a public push. All other model, data, protocol and milestone prerequisites above remain in force.
