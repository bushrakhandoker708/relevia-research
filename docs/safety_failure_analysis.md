# Safety failure analysis

I want Relevia's supportive language to remain useful without presenting uncertain judgements as medical facts. The following investigation was agent-assisted. The regression tests establish specific software behaviour, not clinical suitability.

## Verified routing results

On 7 November 2026, `node scripts/evaluate_safety.mjs --verify` recomputed the frozen S1 result and compared it with the original saved JSON without overwriting it. The original twelve probes are development data: six provisionally urgent, five non-urgent and one ambiguous. S0 missed four urgent cases and raised three false alarms. S1 detects all six and raises no false alarms on these development cases; this is an in-sample correction, not evidence of general reliability.

| Independent synthetic cases, excluding two ambiguous cases | TP | FP | TN | FN |
| --- | ---: | ---: | ---: | ---: |
| S0 original expression | 5 | 6 | 10 | 9 |
| S1 corrected deterministic rules | 11 | 0 | 16 | 3 |

S1 recall is 11/14 = 0.786 (Wilson 95% interval 0.524–0.924), precision 11/11 = 1.000 (0.741–1.000), specificity 16/16 = 1.000 (0.806–1.000), false-positive rate 0/16 = 0 (0–0.194), and false-negative rate 3/14 = 0.214 (0.076–0.476). Zero observed false alarms is compatible with a material population false-alarm rate. These labels were authored and reviewed by the coding agent; they are provisional and not independently clinically validated.

The original misses involved a curly apostrophe, a single-letter omission, a narrow Spanish phrase and an indirect final-goodbye statement. S1 normalises apostrophes, includes the observed omission and phrase, and checks a limited set of indirect expressions. Original false alarms involved an explicit negation and educational discussion of suicide. S1 scopes negation to specific clauses and handles benign context. It also considers the last two user turns for explicit imminent continuations. Assistant template text cannot itself perpetuate an urgent label.

Three held-out misses remain: `heldout-04` (giving possessions away and no future after tonight), `heldout-16` (the spelling `su1cidal`), and `heldout-18` (French language). These demonstrate incomplete indirect, orthographic and multilingual coverage. They were not patched into the frozen detector after test inspection. Any successor needs a new version and genuinely fresh test cases. Cases concerning dependence, harmful agreement and unsupported reassurance do not become safe merely because their urgent-routing label is negative; response safety requires separate review.

## Defect register

| Severity and source | Reproduction and observed behaviour | Expected behaviour and cause | Correction and verification |
| --- | --- | --- | --- |
| P0: `src/services/safety.js` | Run the frozen development probes with S0: four misses, three false alarms | Inspect scoped language/context rather than matching every risk word; restrictive expressions and absent context caused demonstrated errors | Existing S1 corrections reproduced; safety and inference tests pass. Three held-out misses remain |
| P0: `src/pages/About.jsx` | Read symptom explanations: lungs described as fine, chest discomfort described as not heart-related | A static page cannot determine the reader's diagnosis; unconditional reassurance conflated possible anxiety symptoms with confirmed cause | Replaced with uncertainty and appropriate assessment guidance; `tests/content-safety.test.js` prevents specific claims recurring |
| P0: `src/pages/Resources.jsx` | Practical steps told readers to increase heartbeat/dizziness and infer anxiety from improvement with movement | Do not prescribe symptom provocation or treat an exercise as diagnosis | Removed provocation, diagnostic shortcut and unsupported recovery anecdote; content regression test passes |
| P1: exercise scripts | Search coping components for unconditional safety and lasting-calm promises | Optional exercises cannot establish surroundings, safety or outcome | Replaced several absolute assurances with permission to pause and conditional participation. Broader clinician/content review remains open |
| P1: `src/components/ErrorBoundary.jsx` | Error screen guaranteed data/progress were unaffected and displayed an unqualified US number | A crash may lose unsaved work; location is unknown | Replaced guarantee and country assumption; content regression test passes |
| P1: `src/components/Chatbot.jsx` | Historical handler checked the ordinary message limit before safety routing | Deterministic support must remain reachable after the ordinary conversation limit | Previous committed fix keeps the input available at that limit. Browser confirmation is pending; input is still disabled during generation |
| P1: frozen pilot timing | Inspect `test-03`, condition B: 527.946 seconds | Timing should distinguish loading, tokenisation and generation and log scheduling context | Original measurement preserved; repeat protocol and instrumentation added. Historical cause remains unestablished |
| P1: full-project lint | Run full ESLint: initial report retains unused-symbol errors and hook warnings | Runtime callbacks should use current state; dead code should be removed without suppressing rules | Full JSON saved before lint edits; final status belongs in completion report |

The NHS describes overlapping symptoms and the need to assess alternative causes: [panic disorder](https://www.nhs.uk/mental-health/conditions/panic-disorder/), accessed 7 November 2026. This supports avoiding a diagnosis from a page; it does not constitute clinical review of Relevia. Exact text changes are preserved in `results/completion_2026_11_07/content_changes.json` so the original concern and replacement can be inspected.

Browser verification remains unavailable under the previously documented tool restrictions. The user accepted this only for local research. Unverified lifecycle, rendering and multi-tab interactions remain public-release blockers. The archived dataset remains excluded; synthetic routing accuracy does not resolve its provenance.
