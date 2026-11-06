# Milestone 3: dataset integrity and controlled prompting

Date: 5 November 2026. This report describes agent-assisted local research. No commit, push, deployment, LoRA training, learned routing or major UI change was performed. The browser exception remains limited to local research.

## Why this stage follows the privacy foundation

I want the model comparison to answer a question about prompting rather than inherit errors from storage or dataset construction. Both repositories were clean at the start of this milestone on `research/privacy-foundation`: application commit `57cb4cae65ec18eaee84f5aa7df665b9f2f8c543` and research commit `3c5656ab0982d7795bea3010b1d810bf2824ff67`. These are separate histories. The user’s accepted browser exception permits local research, while quarantine prevents the unresolved archive from entering the experiment.

## Repeated Milestone 2 checks

The recorded preflight passed 18 JavaScript tests and eight existing Python tests, changed-file lint, the production build, dataset rebuilding and leakage checks. The new integrity/analysis checks subsequently increased the Python suite to 15 passing tests. Full application lint still fails with 41 errors and nine warnings. Build warnings concern dependency code, old browser metadata and large chunks; a successful bundle is not a clean-install or browser-verification result.

The deterministic safety probes execute successfully but retain four missed provisional-risk cases and three false alarms. They do not validate clinical safety. The redacted scanner found no selected-pattern or known-local-value credential matches in 199 application blobs, 102 research blobs and 31 compiled files. Unreachable or unavailable history, external deployments and other secret formats remain outside that claim.

## Data integrity decision

The original archive instructions mislabelled EmpatheticDialogues as MIT. The official EmpatheticDialogues and ESConv licences are CC BY-NC 4.0; ESConv also states academic-research-only use. The [provenance report](dataset_provenance_report.md) distinguishes dataset-level publication terms from individual consent or an archive-specific source chain.

The 15,000-row archive has 26 duplicate normalised pairs and 4,337 repeated prompts. Although its text strongly matches the local training source, its row-level provenance and pairing remain unresolved. It was moved without byte changes to `archive/quarantine/empathy_42k.jsonl.quarantined`. Its digest is recorded and experimental access is prohibited. Existing Git history still contains it; quarantine is not redistribution clearance.

Active EmpatheticDialogues data have zero conversation-group overlap and zero normalised pair overlap across all 15 partition pairs. Frozen test hashes remain unchanged. The synthetic pilot has four development groups and eight test groups, no group/input overlap and no few-shot examples. Its card explicitly identifies agent authorship and review limits. No real conversations are used for model generation.

## Controlled baseline and failures preserved

Llama-3.2-1B-Instruct was preferred but was not locally available and has manually gated access. The implementation instead uses the public Qwen2.5-1.5B-Instruct checkpoint at revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, under Apache-2.0, on CPU float32 with eight threads. Both conditions use identical weights, tokenizer, seed, greedy decoding, inputs and a 110-token budget. The developed prompt is the sole intended response-generation treatment.

Two development rounds were recorded. The first produced two token-limit hits for A and one for B. After a development-only brevity/grounding revision, B had none while A retained two. Unsupported details remained, so the revised prompt is not described as a solved or globally optimal policy. The configuration, data, rubric and runner were frozen before test generation.

The first development load attempted optional network metadata queries despite a local-only principal load. Offline flags were added before later runs. A restricted-network DNS failure was resolved for the authorised public model download; local generation does not require uploading dialogue. The Jupyter-kernel attempt did not complete during observation and was interrupted. Report notebooks execute actual Python cells through a documented sequential executor, with real expression output and matplotlib images; no Jupyter-kernel success is claimed.

One frozen-test generation recorded approximately 528 seconds. The cause is not established; it is retained rather than removed as inconvenient. CPU contention, suspension and other timing causes are possibilities, not verified explanations. Means, medians and ranges describe the run, not model speed or browser performance.

## Reading the evidence

The executed [dataset audit](../notebooks/01_dataset_audit.ipynb) and [baseline notebook](../notebooks/03_baseline_evaluation.ipynb) explain the choices, measurements, failures and limits. Test responses, configuration and execution status live under `results/experiment_01/`. The initial ratings are unblinded coding-agent assessments using the frozen draft rubric; they are not independent human ratings or clinical evidence. The prepared blinded review packet has empty scores and has not been sent to anyone.

No LoRA readiness follows from a small pilot or a favourable mean. The highest-value next action is independent blinded review of the frozen response pairs, followed by the user’s approval of the baseline and supporting evidence before any training.


## Recorded Experiment 01 outcome

All 16 test outputs were generated, with zero runtime failures. These are actual Qwen outputs, not stub responses. The following ratings are unblinded agent assessments and require independent review.

| Dimension | Mean paired B−A | 95% group-bootstrap interval |
|---|---:|---|
| relevance | +0.125 | -0.875 to 1.125 |
| emotional acknowledgement | +0.125 | 0.000 to 0.375 |
| clarity | +0.875 | -0.125 to 1.875 |
| practical helpfulness | -0.125 | -0.500 to 0.250 |
| autonomy | -0.125 | -0.750 to 0.375 |

The primary relevance interval crosses zero, so the pilot does not establish that B improves relevance. Practical helpfulness and autonomy have slightly negative point estimates. B has zero token-limit hits versus four for A, but shorter output is not an overall quality result. One A output ends cleanly at the limit; budget exhaustion and visible truncation are distinct.

Both A and B received an inadequate-escalation flag on the single immediate-risk scenario. B also received a provisional dependency/role-boundary flag for offering a shared movie activity. These counts use eight outputs per condition; they are not population safety rates. The medical-boundary case shows a rubric gap: speculative diagnostic framing can be concerning without a definite diagnosis, so zero medical-claim flags do not clear the replies. The full reasons are preserved in `agent_ratings.json`.

A’s mean/median elapsed time was 32.67/36.73 seconds; B’s was 87.72/28.05 seconds. B includes the unexplained 527.95-second outlier. No runtime advantage is claimed. No clinical benefit, comprehensive safety or LoRA readiness follows from this convenience sample. The paired notebook, frozen artifacts and blank blinded rating sheet are ready for review.

See [commands and reproduction](milestone_3_commands.md) and `results/milestone_3/changed_files.txt` for the complete command and file inventories. Public release still requires browser verification and content review. Further model development remains behind the user’s approval of this baseline.

## Completion work: independent review preparation

On 6 November 2026, Bushra confirmed that reviewers were unavailable and asked for prepared materials. Two separately randomised blank packets now contain six responses each from three ordinary-context pilot scenarios. Bereavement, caregiving, aggression, medical requests and immediate distress are excluded from this preliminary packet. The [coordinator instructions](independent_review_coordinator.md) explain distribution, missingness, blinding limits and preservation of returned ratings. No materials have been sent externally and no human scores exist.

The new rubric adds grounding without changing the original pilot ratings. This subset is not the expanded independent evaluation: there are only three independent scenarios. Milestone 3 completion remains partial, with independent review, expanded evaluation, runtime investigation and the remaining engineering checks still outstanding. The user has not approved LoRA training or public release.
