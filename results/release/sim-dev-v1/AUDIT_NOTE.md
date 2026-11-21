# Audit note, 21 November 2026

This run is kept unchanged as the record of what was done. An audit found that 177 of its 201 traces were replies to inputs that must not be used for design:

| Corpus | Traces | Generated on | Status of that input |
|---|---|---|---|
| `experiment_01/expanded-v1` | 121 | `data/experiment_01_expanded/test.jsonl` | Test-only (dataset card) |
| `safety/generative-v1` | 45 | `data/safety_v3/heldout.jsonl` | Held-out safety set |
| `performance/repeat-v1` | 11 | `data/experiment_01/test.jsonl` | Final test set |
| `experiment_01/dev-v1`, `dev-v2`, `lora/smoke-v1-generations` | 24 | `data/experiment_01/dev.jsonl` | Development |

The README's statement that the final test set was left out is true only for `experiment_01/test-v1`; the `performance/repeat-v1` replies come from the same test inputs. The one reply that both R2 and R3 blocked is from the held-out safety set.

Only latency was computed, from reply length and sentence boundaries, with simulated timing and no labels, and the policy code was not changed in response to the run as far as the record shows. The practical consequence is that these three inputs should not be used to evaluate R0–R3 in the study, or, if they are, they must be reported as seen during development. `simulate_traces.used.mjs` is the exact script that produced `traces.json` (it regenerates it byte for byte, SHA-256 `422219f2…`). The development-only rerun is `../sim-dev-v2/`. Full audit: `docs/REPRODUCIBILITY_AUDIT_2026-11-21.md`.
