# Claim–evidence matrix

Each claim in `manuscript.md` is listed with the evidence that supports it and how strong that evidence is. If a claim has no row here, it should not be in the manuscript.

| # | Claim | Evidence | Strength | Missing for a stronger claim |
|---|---|---|---|---|
| 1 | Data partitions are conversation-separated | `scripts/check_leakage.py`: 0 overlap across 15 pairs; re-run 7 Nov | Strong (deterministic check) | none for this claim |
| 2 | The historical archive is excluded | `data/quarantine_manifest.json` hash; no active path reads it | Strong | provenance of the archive itself |
| 3 | A and B differ only in the system prompt | `configs/expanded.freeze.json`, run manifests | Strong | none |
| 4 | B hits the token cap far less often than A | 1/60 vs 30/60, McNemar p = 3.7e-9 (`robustness.json` E3) | Strong for this model, input set and cap | other models and input sets |
| 5 | B's apparent latency advantage comes from shorter replies | B slower per token (54/58 pairs) and to the first token (57/58), yet 19 tokens shorter (E2) | Moderate: one machine, CPU only | browser replication |
| 6 | The original latency interval was distorted by host suspension | Modern Standby window overlaps 2 pairs (F1) | Moderate: the cause of the 527.9 s pilot outlier is still unexplained | power-state logging in future runs |
| 7 | S2 detects more v3 urgent messages than S1 without new false alarms | 18/24 vs 9/24; FPR 0/18 for both (`s2-v1/evaluation.json`) | Weak to moderate: same agent wrote v3 and S2; n = 42 | an independently written frozen set |
| 8 | The LoRA pipeline runs end to end without reading the final test set | `results/lora/smoke-v1/manifest.json`: `final_test_read: false`, val loss 4.02 → 3.67 | Pipeline check only | the approved pilot |
| 9 | The reply guard catches the logged failure | `relevia/tests/reply-guard.test.js` (11 tests) | Unit-level | live monitoring of real replies |
| 10 | Benchmark instrumentation separates startup, TTFT, prefill/decode, failures and unloading | 5 unit tests; one real run (`results/performance/browser-v1-intel/`) | One laptop, Intel iGPU, 3 repeats | RTX 4060 run after the Windows GPU setting; more devices |
| 10a | Lexical flags miss the most serious generative failures | 4 of 6 S2-missed urgent replies read as inadequate, 0 flagged (`results/safety/generative-v1/analysis.json`, `docs/safety_failure_taxonomy.md`) | Weak: agent reading, n = 6 | independent hazard ratings |
| 10b | S3 routes far more urgent messages than S2 without new false alarms | v4 first run: 43/46 vs 13/46, FP 0/25 vs 2/25; McNemar p ≈ 1.5e-8 (`results/safety/s3-v1/`) | Moderate: frozen before S3, but same author; n = 71 | an independently written set |
| 10c | S3 rarely over-routes ordinary human text | ED dev 2,873 prompts: 1 urgent false alarm, 0 emergencies (`results/safety/s3-v1-ed-scan/dev_heldout.json`) | Moderate for over-routing; says nothing about recall | other corpora, multi-turn text |
| 10d | Emergencies get a non-generative emergency message in the app | browser UI check 8 Nov; `tests/safety-s3.test.js` | Functional | wording review by a qualified person |
| 10e | G2 had fewer errors than G1 on real replies. G2 could still show an unfinished sentence that was later rejected ("Child" → "Childline"). G3 shows only finished sentences that have passed the check, at a measured cost of a median 2.6 s before the first text appears | 218 replies (`results/safety/reply-guard-v1/`, `audit_g3.json`); app tests that check every prefix of 10 replies | Weak: 2 positives in the corpus; G3's lag was simulated at 5.6 tok/s, not measured in a browser | a larger corpus with refusals and numbers; in-browser timing |
| 10f | Prior work found fine-tuning helps small models' empathy | BN et al. 2025 abstract only | Weak: abstract | full text; earlier contrary note withdrawn |
| 11 | B is more supportive than A | none | **Not supported** | 2 independent blinded reviewers, 120 items |
| 12 | C is more supportive or safer than B | none | **Not supported** | approved pilot, final-test generation, ratings |
| 13 | The work is novel | none | **Not supported** | completed literature review |
