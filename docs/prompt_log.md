# Prompt tuning log

This log records proposed and executed prompt changes separately. New prompt development uses **dev** only; validation is reserved for model selection and test sets remain isolated. The earlier instruction to tune on validation was incorrect and is superseded by the Milestone 2 leakage correction. The original entry below remains unexecuted. No result should be inferred from its presence.

| Version | Date | Change | Recorded result (historical entry) | Kept? |
|---|---|---|---|---|
| v1 | 2026-11-03 | First version: reflect feeling → show understanding → one question; honesty + crisis instructions | not run yet | — |


## Experiment 01 development review — 5 November 2026

The agent reviewed eight actual responses from four synthetic development cases in `results/experiment_01/dev-v1`. A reached the 110-token limit on two cases and B on one. Both introduced unsupported details: the friendship replies assumed unexpected cancellation or no prior notice, and the dependence replies inferred unreported emotional or relationship difficulties. B was therefore revised to require 2–4 complete sentences, at most 65 words, no lists/placeholders, only supplied details and no generic motivational ending. This change uses development outputs only. It is a candidate correction, not evidence of improved test performance. A retains the same minimal safety prompt. The revised configuration is rerun on development before freezing.


The second development run completed all eight responses. B had no token-limit hits, while A retained two. B still assumed unexpected cancellation and misunderstanding by others, and did not consistently obey the wording/length constraints. The candidate is frozen as B revision 2 to evaluate its limits rather than continue adapting it to four cases. No improvement in independent quality is claimed from this development decision. Eight separate synthetic test cases, the configuration, rubric and runner are locked in `configs/experiment_01.freeze.json` before test generation.
