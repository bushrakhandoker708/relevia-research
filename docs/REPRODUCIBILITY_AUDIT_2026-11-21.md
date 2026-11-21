# Reproducibility audit, 21 November 2026

*Agent-run audit for Bushra's review. It checks whether the release-policy work kept development and evaluation data apart, whether the code it ran can be recovered, and whether the LoRA pipeline's safeguards are in place. It does not re-run any model.*

## 1. Were test or held-out outputs used to develop the release policies?

**Yes, in the development replay.** `results/release/sim-dev-v1/` was described as a run on "six development corpora" with the final test set left out. Checking each corpus's manifest against the input files it was generated from gives a different picture:

| Corpus | Replies | Generated on | Role of that input |
|---|---|---|---|
| `experiment_01/expanded-v1` | 121 | `data/experiment_01_expanded/test.jsonl` | Test-only: its dataset card forbids prompt tuning, selection, training and early stopping on it, and `configs/milestone_4.pilot.json` names it as the LoRA final test |
| `safety/generative-v1` | 45 | `data/safety_v3/heldout.jsonl` | Held-out safety set |
| `performance/repeat-v1` | 11 | `data/experiment_01/test.jsonl` | The final test inputs (same SHA-256, `769d2139…`) |
| `experiment_01/dev-v1`, `dev-v2`, `lora/smoke-v1-generations` | 24 | `data/experiment_01/dev.jsonl` | Development |

So 177 of the 201 replies were test or held-out material. `experiment_01/test-v1` was excluded, but `performance/repeat-v1` contains replies to the same test inputs. The one reply blocked by R2 and R3 came from the held-out safety set.

**How much it matters.** The replay used only the length and sentence structure of each reply, with simulated timing and no labels, so no exposure figure and no threshold was fitted to these replies. The R3 code was already written; nothing in the record shows it was changed after the run. The run did, however, inform a design decision: the protocol's condition that R3 must beat R2 by at least 1 s before it is worth testing (section 6) was first checked on it.

**What was done.**

- `sim-dev-v1` is unchanged. An `AUDIT_NOTE.md` beside it records the finding, and `simulate_traces.used.mjs` is the exact script that produced it; it regenerates `traces.json` byte for byte (SHA-256 `422219f2…`).
- `scripts/simulate_traces.mjs` now reads only development corpora and checks each corpus's input hash against lists of development and protected files. It stops if a corpus is test or held-out data, or if its inputs cannot be shown to be development data. `--check` confirms that the corpora above are refused.
- `results/release/sim-dev-v2/` repeats the replay on the 24 development replies. R3's median time to first visible text was 0.23 s against 2.78 s for R2, with a gain of at least 1 s on 21 of 24 replies. The gap seen in `sim-dev-v1` is therefore not an artefact of the test material, but 24 replies from one model and one prompt family is a small base, and the timing is still simulated.

**Consequence for the study.** The protocol already plans new browser-recorded streams with their own development and test sets. Those new sets must be authored and frozen before any release-policy work looks at their replies. The three protected inputs above should not be used to compare R0–R3; if they are, they must be reported as seen during development.

## 2. Every existing reply has been read during guard development

`scripts/audit_reply_guard.mjs` runs the reply guard over all 218 saved replies, including `experiment_01/test-v1` and `expanded-v1`, and its header already says so: "The 218 replies have been read during guard development, so every result here is development evidence, not a held-out test." The 21 November G3 change followed that audit.

This is recorded honestly, but its consequence is worth stating plainly: **no existing reply set can serve as held-out evidence for the reply guard or for R0–R3.** It does not by itself invalidate the planned independent quality ratings of prompts A and B on the test sets, because the prompts were revised on the development set before those replies were generated (the expanded-v1 manifest records `B-dev-revision-2`) and the guard plays no part in rating. Reviewers should still be told that an agent has read the replies.

## 3. Can the code that produced the release results be recovered?

Before this audit, `scripts/replay_release.mjs` imported the policies from the live application checkout and recorded their hashes. The hashes made a later mismatch detectable, but the files themselves could have moved on.

- `detectors/release_v1/` now holds byte-identical copies of `releasePolicy.js`, `replyGuard.js` (G3) and `consts.js` from application commit `3195335`. Their hashes match the ones recorded in `sim-dev-v1/replay.json`.
- The replay now uses these frozen copies by default and records which source it used. `--app <dir>` still runs against an application checkout, for development.
- `tests/test_replay_release.py` checks the frozen hashes and no longer needs the application checkout, so it can run in CI.

## 4. LoRA pipeline

Checked against `scripts/lora_pilot.py`, `configs/milestone_4.pilot.json` and commit `c164cac`:

- `training_enabled` is `false`, and `--pilot` refuses to run without `--approved-by`. No pilot has been run in this round.
- Learning-rate candidates (1e-4, 2e-4) are to be chosen on a frozen subset of the EmpatheticDialogues validation partition, whose SHA-256 is now checked. The final test is `data/experiment_01_expanded/test.jsonl`, which is not used for selection.
- The fixes in `c164cac` (validation loss weighting, the final partial accumulation step, adapter folders never overwritten, truncated replies recorded) have tests in `tests/test_lora_pilot.py`, which pass.
- Not checked: whether the pinned versions in `requirements-lora-tested.txt` still install, because that needs a download.

## 5. Not covered

- Model outputs were not regenerated, so determinism of generation was not re-tested.
- The integrity of `data/` files other than those named above was taken from their recorded hashes, not re-derived.
- This audit was carried out by the same kind of agent that wrote much of the code it checks. An independent check by a person would be stronger.
