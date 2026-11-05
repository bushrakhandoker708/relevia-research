# First milestone: establish a defensible baseline

This document distinguishes work completed in the initial response from the next implementation gate. It deliberately does not authorize claims that the whole Phase 0 is finished.

## Completed initial deliverable

Created architecture_audit.md, known_issues.md, privacy_and_threat_model.md, decision_log.md, experiment_dependency_map.md, notebook_blueprint.md and research/notes/LITERATURE_REVIEW.md. Added scripts/audit_snapshot.py and scripts/probe_safety.mjs. Preserved existing app source and research history. The proposed introduction is supplied for author review in chat rather than inserted into a final research report.

From the supplied workspace root, reproduce the dependency-free diagnostics:

```powershell
git -C relevia rev-parse HEAD
git -C relevia-research rev-parse HEAD
python relevia-research/scripts/audit_snapshot.py
node relevia-research/scripts/probe_safety.mjs
npm --prefix relevia run build
npm --prefix relevia run lint
```

Outputs: results/audit/snapshot.json and safety-probes.json under this repository. Build writes app dist; lint currently fails. The Python audit checks syntax, not runtime imports or GPU compatibility. Its secret screen is pattern-based, excludes blobs over 2 MB and does not inspect unreachable history, provider status or all generated bundles. No zero-findings result should be called a clean security audit.

## Next implementation gate — exact changes

1. `../relevia/src/services/db.js`: replace unsupported DP claim; introduce an explicit storage policy, session-only default, per-profile isolation, read-time expiry and versioned deletion/migration behavior.
2. `../relevia/src/services/releviaBrain.js`: preserve crisis-first routing; avoid automatic persistent crisis storage; remove raw-content logs; return response provenance; invalidate pending persistence on deletion.
3. `../relevia/src/services/personalLetter.js`: consume only permitted, unexpired context; no unsolicited sensitive follow-up on the Home page.
4. `../relevia/src/components/Chatbot.jsx`: visible AI/non-clinical disclosure; retention choice and deletion; distinguish curated from generated replies; remove content logging. Preserve layout and grounding tools.
5. `../relevia/src/services/groqApi.js`: remove unused frontend integration from production source after import verification; preserve history. Do not replace it with a cloud backend without a research need.
6. `../relevia/src/services/memoryUtils.js`, `safety.js`: review curated claims first; do not call new regex rules validated. Add location choice and reviewed source maintenance separately from risk detection.
7. `../relevia/README.md`: correct privacy, fine-tuning, notebook, size and compatibility statements against verified behavior.
8. `../relevia/tests/storage.test.js`, `tests/response-provenance.test.js`: test expiry, identity isolation, legacy migration, consent withdrawal, deletion races, unavailable storage and model failure. Choose and pin an IndexedDB test shim after dependency review; browser tests remain necessary.

MUST verification: test a returning profile after expiry without a new write; two isolated profiles; deletion during pending generation; no raw text/name in production console; fallback and crisis provenance; no model invocation for a matched urgent case. Run build and lint, inspect actual browser storage/network, and update issue statuses with evidence. Fix lint configuration before counting JSX identifiers as truly unused.

TARGET: a clean install from the existing lockfile in a disposable verification directory and a 20–40-case synthetic **development** baseline. STRETCH: browser latency instrumentation. No new model training or website redesign is needed before the 9 November coursework deadline.

## Following research changes

`data/build_dataset.py`: reserve entire few-shot conversation groups, audit all partitions, generate source/license/checksum manifest, record excluded/truncated rows. `configs/base.yaml` and `configs/models/llama-3.2-1b.yaml`: exact revisions and validated decoding/training schema. `src/common.py`: resolve and log effective configuration. `src/generate.py`: record prompt/data hashes, revision, environment, seed and failures without overwriting completed runs. `src/make_rating_sheet.py`: require explicit A/B/C completeness and use the approved 1–5 rubric with separate safety labels.

Use B=`tuned_prompt`, C=`finetuned_tuned` as primary. Hold training-data provenance, evaluation data, prompts and inference configuration fixed. Training with plain versus tuned prompts is itself a design choice to record; do not silently change it during final experiments.

## Completion checklist

- [x] Source revisions and actual layout identified.
- [x] Required application services inspected; existing research implementation reviewed.
- [x] Local build and lint outcomes recorded; diagnostic detector failures reproduced.
- [x] Initial research gap, dependencies and notebook blueprint written.
- [ ] Full history/artifact credential audit and any required provider rotation.
- [ ] Privacy controls implemented and browser-tested.
- [ ] Clean environment and passing regression gate.
- [ ] Licensed data manifest, reviewed labels and frozen evaluation protocol.
- [ ] Model quality, training, performance or routing results.

The highest-priority next action is the storage/privacy patch with regression tests. For an interview, be able to explain why local inference is not differential privacy, why B/C needs an identical prompt, why dialogue turns are correlated observations, and why a build passing is not evidence of safe model behavior.
