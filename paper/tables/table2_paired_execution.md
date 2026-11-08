# Table 2. Paired B − A execution differences (expanded-v1, CPU float32)

Generated from `results/analysis/robustness-v1/robustness.json`. Execution measures only; no quality ratings exist.

| Measure | Pairs | Median | Hodges–Lehmann | B larger / B smaller | Sign test p |
|---|---|---|---|---|---|
| End-to-end latency (s), all pairs | 60 | -3.652 | -3.500 | 22 / 38 | 0.052 |
| End-to-end latency (s), standby excluded | 58 | -3.347 | -3.169 | 22 / 36 | 0.087 |
| Time to first token (s) | 58 | 2.415 | 1.960 | 57 / 1 | 4.1e-16 |
| Seconds per output token | 58 | 0.050 | 0.049 | 54 / 4 | 3.2e-12 |
| Output tokens | 58 | -19.000 | -19.000 | 13 / 43 | 7.3e-05 |
