# Release-policy replay on simulated streams (development only)

21 November 2026. Agent-run development check of `scripts/replay_release.mjs`, not a study result.

**Inputs.** 201 saved model replies from six development corpora (`traces.json`, built by `scripts/simulate_traces.mjs`). The final test set `experiment_01/test-v1` was left out so that it plays no part in designing R3. Timing is **simulated**: one word per chunk at 5.6 tok/s and 1.3 tokens per word, first word at 0.23 s. The replies carry **no unsafe-span labels**, so this run measures latency only. It says nothing about exposure or false interventions.

| Policy | First visible text, median | 95th percentile | Completion, median |
|---|---|---|---|
| R0 immediate | 0.23 s | 0.23 s | 14.9 s |
| R1 whole reply | 14.9 s | 21.6 s | 14.9 s |
| R2 sentences (app, G3) | 2.55 s | 4.87 s | 14.9 s |
| R3 prefix-safe | 0.23 s | 0.46 s | 14.9 s |

R3 showed text sooner than R2 on most replies: median gain 2.1 s, and at least 1 s on 82% of them. Both policies blocked the same reply (the logged refusal), and the policy check cost about 0.01 ms per call in Node.

**What this does and does not show.** On these replies R3 recovers most of the delay R2 added, which is the condition the protocol sets before R3 is worth testing. Whether R3 shows more unsafe text than R2 is unknown until replies with independent span labels are replayed. R3 releases the unfinished sentence whenever no rule could still act on it, so any harmful wording the rules do not describe reaches the screen sooner than under R2. Real browser chunks are uneven, so the true gain will differ.

Code hashes are recorded in `replay.json` (`code`). R0–R3 are in the application at `src/services/releasePolicy.js`; freeze a copy under `detectors/` before the study.
