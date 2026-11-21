# Release-policy replay on simulated streams, development replies only

21 November 2026. Agent-run development check, not a study result. It replaces `sim-dev-v1` as the development reference, because `sim-dev-v1` read replies to test and held-out inputs (see `docs/REPRODUCIBILITY_AUDIT_2026-11-21.md`). `sim-dev-v1` is kept unchanged as the record of what was run.

**Inputs.** 24 saved replies from three corpora, each checked by `scripts/simulate_traces.mjs` against the input files it was generated from (`traces.provenance.json`): `experiment_01/dev-v1`, `experiment_01/dev-v2` and `lora/smoke-v1-generations`, all on `data/experiment_01/dev.jsonl`. Timing is **simulated** exactly as in `sim-dev-v1`: one word per chunk at 5.6 tok/s and 1.3 tokens per word, first word at 0.23 s. The replies have **no unsafe-span labels**, so this measures latency only.

**Code.** The policies and guard are the frozen copies in `detectors/release_v1/` (hashes in `replay.json`, `code`).

| Policy | First visible text, median | 95th percentile | Completion, median |
|---|---|---|---|
| R0 immediate | 0.23 s | 0.23 s | 14.9 s |
| R1 whole reply | 14.9 s | 21.1 s | 14.9 s |
| R2 sentences (app, G3) | 2.78 s | 3.02 s | 14.9 s |
| R3 prefix-safe | 0.23 s | 0.23 s | 14.9 s |

R3 showed text sooner than R2 by a median of 2.3 s, and by at least 1 s on 21 of the 24 replies. No reply was blocked by any policy. With 24 replies from one model and one prompt family, and timing that is simulated rather than recorded, this only confirms that the latency gap seen in `sim-dev-v1` is not an artefact of the test material. It says nothing about exposure, which needs labelled traces.
