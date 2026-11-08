# Milestone 3 closure

Date: 8 November 2026. This is an agent-assisted audit for Bushra's review. It records what Milestone 3 completed, what remains unverified and what is explicitly deferred. Its purpose is to make it clear what Milestone 4 may rely on. It does not change any earlier result.

## State inspected

Both repositories were on `research/privacy-foundation`, with `main` fast-forwarded to the same commits: the application at `0b8df47` and the research repository at `286bd42`. Both working trees were clean before Milestone 4 began. The two histories remain separate. The application's `src/services/safety.js` is now S2. The S1 detector used by the Milestone 3 safety evidence is preserved byte-for-byte in `detectors/s1/`, and `node scripts/evaluate_safety.mjs --verify` still reproduces the saved S1 results.

## Verification

| Item | Status | Evidence |
|---|---|---|
| Dataset provenance and licence | **Complete for the active data.** EmpatheticDialogues is CC BY-NC 4.0 (not MIT, as the original archive notes claimed). The 15,000-row historical archive remains quarantined, with its hash recorded. | `docs/dataset_provenance_report.md`, `data/quarantine_manifest.json` |
| Development, validation and test independence | **Complete.** All 15 partition pairs have zero group overlap and zero normalised pair overlap. The synthetic pilot and the 60-case extension have no group or input overlap with development; the token-Jaccard check (threshold 0.65) found no near duplicates. The checks were re-run on 7 November with identical results. | `scripts/check_leakage.py`, `scripts/check_experiment_01.py`, `scripts/check_expanded_integrity.py` |
| Model identity | **Complete.** `Qwen/Qwen2.5-1.5B-Instruct` at revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, Apache-2.0, loaded offline from the local cache. | `configs/experiment_01.pilot.json` |
| Prompt versioning | **Complete.** A is the minimal safe prompt. B is `B-dev-revision-2`, frozen after two development rounds that used development data only. | `docs/prompt_log.md`, `configs/expanded.freeze.json` |
| Generation parameters | **Complete.** Greedy decoding, 110 new tokens, seed 42, CPU float32, eight threads. They are identical for A and B. | run manifests |
| Executed outputs | **Complete.** The pilot has 16 outputs, the extension 120 and the repeat-timing run 10, with no runtime failures. All raw responses are kept. | `results/experiment_01/*/responses.jsonl`, `results/performance/repeat-v1/` |
| Safety failure documentation | **Complete as development evidence.** S0 to S1 to S2 routing, the perturbation probe and the remaining S2 misses are recorded. Detector labels are agent-authored and provisional. | notebooks 05, 07 and 08, `results/safety/` |
| Test logs | **Passing.** 32 Python tests and 70 application tests pass. Full application lint still has legacy failures outside the changed files. | `results/completion_2026_11_07/`, local runs on 8 November |
| Independent evaluation | **Not done.** Both blinded reviewer sheets for the extension have 0 of 120 items rated. No human ratings exist anywhere in the project. | `results/experiment_01/expanded-v1/reviewer_*/ratings.csv` |

## What the evidence supports

The original eight-scenario pilot stays exactly as recorded: exploratory evidence with *unblinded agent* ratings. Its relevance difference of +0.125 (95% interval −0.875 to +1.125) does not show that B improves relevance. It must not be described as independent human evaluation.

The 60-scenario extension supports execution-level statements only. A reached the token cap in 30 of 60 replies and B in 1. B costs about 2.4 s more before the first token and more time per token, and it appears faster overall only because it writes less (notebook 07). The earlier headline latency interval was dominated by two pairs that overlapped Windows Modern Standby. There is no quality result.

## Unverified or deferred

- **Independent blinded ratings.** These are the gate for any quality claim, including the planned B vs C comparison. Reviewers are not currently available.
- **Browser inference.** Every model measurement so far is Python on CPU. The 8 November app check found that this laptop's browser uses the Intel UHD integrated GPU even though an RTX 4060 is installed (decode about 1.5 to 2.7 tok/s). Windows controls this choice, and no browser benchmark has been run.
- **Clinical validity of any safety label.** This is deferred and out of scope for the project as it stands.
- **The cause of the 527.9 s pilot outlier.** This is unexplained. A Modern Standby overlap explains the 956.7 s observation in the extension, not this one.

## Decision

Milestone 3 is closed **as exploratory groundwork**, not as a validated baseline. Milestone 4 may prepare and smoke-test the LoRA pipeline, because nothing in that preparation depends on quality ratings. It may not report a B vs C quality result, or select adapter settings on the final test set, until independent ratings of the baseline exist or Bushra explicitly accepts a narrower exploratory objective.
