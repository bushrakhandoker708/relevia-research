# Table 1. Routing on the frozen v3 held-out set

Generated from `results/safety/s2-v1/evaluation.json`. Labels are agent-authored and provisional; 3 ambiguous cases are excluded.

| Detector | TP | FN | FP | TN | Recall (95% Wilson) | FPR (95% Wilson) |
|---|---|---|---|---|---|---|
| S0 | 13 | 11 | 3 | 15 | 0.54 (0.35–0.72) | 0.17 (0.06–0.39) |
| S1 | 9 | 15 | 0 | 18 | 0.38 (0.21–0.57) | 0.00 (0.00–0.18) |
| S2 | 18 | 6 | 0 | 18 | 0.75 (0.55–0.88) | 0.00 (0.00–0.18) |

| Category | S0 | S1 | S2 |
|---|---|---|---|
| shorthand | 3/5 | 3/5 | 5/5 |
| no_apostrophe | 4/4 | 2/4 | 3/4 |
| dropped_g | 0/1 | 0/1 | 0/1 |
| stretch | 2/2 | 0/2 | 1/2 |
| typo | 0/3 | 1/3 | 3/3 |
| caps | 1/1 | 0/1 | 0/1 |
| leet | 0/1 | 0/1 | 1/1 |
| split_word | 1/1 | 1/1 | 1/1 |
| plain | 3/3 | 2/3 | 3/3 |
| indirect_hard | 0/2 | 0/2 | 0/2 |
| third_party | 1/2 | 2/2 | 2/2 |
| zero_width | 0/1 | 0/1 | 1/1 |
| idiom | 5/5 | 5/5 | 5/5 |
| benign_overlap | 3/3 | 3/3 | 3/3 |
| technical | 1/1 | 1/1 | 1/1 |
| ordinary_distress | 2/2 | 2/2 | 2/2 |
| negation | 0/1 | 1/1 | 1/1 |
| history | 0/1 | 1/1 | 1/1 |
| academic | 0/1 | 1/1 | 1/1 |
| fiction | 1/1 | 1/1 | 1/1 |
| ordinary | 1/1 | 1/1 | 1/1 |
| ambiguous | 0/0 | 0/0 | 0/0 |
