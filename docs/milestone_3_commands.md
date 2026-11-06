# Milestone 3 commands and execution record

Run from `relevia-research` unless stated otherwise. Existing output directories are immutable run records: choose a new `--out` for reproduction rather than overwriting them. No command below authorises training or publishing.

## Verification and audit

```powershell
python scripts/verify_milestone_3.py
python scripts/audit_dataset_integrity.py
python scripts/check_leakage.py --out results/milestone_3/leakage.json
python -m unittest discover -s tests -v
python scripts/check_experiment_01.py
```

The preflight script runs application `npm test`, scoped ESLint with `--max-warnings 0`, `npm run build`, full `npm run lint`, research safety probes, Python tests, dataset rebuilding, leakage checks and the redacted security scan. See `results/milestone_3/verification.json` for exact commands and exits. Full lint is an explicitly recorded failure, not hidden by the aggregate script status. The first attempt from the outer workspace failed to locate the verification script; the command above ran from the correct directory.

## Model acquisition and paired runs

A public Hugging Face metadata request outside the restricted network verified the Qwen revision. `snapshot_download` fetched the following pinned model into the ignored local cache, with `token=False` and two workers:

```python
snapshot_download('Qwen/Qwen2.5-1.5B-Instruct',
    revision='989aa7980e4cf806f80c7fef2b1adb7bc71aa306',
    cache_dir='.cache/huggingface',
    allow_patterns=['*.json', '*.safetensors', '*.txt', 'LICENSE', 'README.md'],
    max_workers=2, token=False)
```

```powershell
python scripts/experiment_01.py --phase dev --out results/experiment_01/dev-v1
python scripts/experiment_01.py --phase dev --out results/experiment_01/dev-v2
python scripts/experiment_01.py --phase test --out results/experiment_01/test-v1
```

The two development runs used different versions of B. Each manifest embeds the exact configuration. The current configuration is revision 2 and is frozen for test-v1, so replaying it does not recreate the earlier B prompt. Model loading is local-only during generation. The first dev run predates the added offline environment flags; attempted optional network lookups are documented.

## Analysis and notebooks

```powershell
python scripts/analyse_experiment_01.py --run results/experiment_01/dev-v1
python scripts/analyse_experiment_01.py --run results/experiment_01/dev-v2
python scripts/analyse_experiment_01.py --run results/experiment_01/test-v1 --ratings results/experiment_01/test-v1/agent_ratings.json
python scripts/export_experiment_review.py --run results/experiment_01/test-v1 --out results/experiment_01/review
python scripts/execute_report_notebook.py notebooks/01_dataset_audit.ipynb
python scripts/execute_report_notebook.py notebooks/03_baseline_evaluation.ipynb
```

The report executor performs real Python execution, records outputs and fails on an exception. It is used because the attempted Jupyter kernel did not complete during observation and was interrupted. It does not run model generation. Blank independent-review sheets do not constitute completed ratings. Agent ratings are explicit, unblinded annotations of the recorded outputs, not automatic lexical scores or human research data.

Final checks include `git diff --check`, notebook-output inspection, frozen-hash verification and confirmation that the model cache and rating key are ignored. No commit, push or deploy command was run.
