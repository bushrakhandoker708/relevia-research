# Append-only research decision diary

Entries below are proposed author wording grounded in the request and inspected code. They do not attribute unconfirmed personal experiences or historical motivations. Corrections should be new dated entries, not silent edits to earlier conclusions.

## D001 — Preserve both repositories, 2026-11-05

**Context:** The supplied workspace contains an app, a separate research repository and an unborn outer Git repository.

**Evidence:** App SHA d6d2ec2f8ccbeb69b0b992bb24b64af52fed68ce; research SHA 8c3cf54781a3c9552c46bd57e603b57a56a6aae3; public main agrees with app SHA.

**Options:** Flatten into a monorepo; replace research scripts; retain current layout and add an audit.

**Selected approach:** I preserve the layout and add research documentation and diagnostic scripts under the research repository.

**Why selected:** This retains traceable historical work and avoids disrupting coursework. **Why not alternatives:** Restructuring adds migration risk without answering an RQ.

**Implementation:** docs/architecture_audit.md; scripts/audit_snapshot.py. **Verification:** Git status/revisions and archive spot comparison. **Results:** Provenance established; no source rewrite or deployment. **Limitations:** Full archive equality and live deployment not verified. **Practical significance:** Future experiments can cite an actual source state. **Next step:** Commit reviewed audit artifacts separately from application repairs.

## D002 — Audit before adaptation, 2026-11-05

**Context:** Training on an unsafe or irreproducible pipeline cannot establish useful improvement. **Evidence:** Shared storage, unsupported privacy claim, failing lint and diagnostic safety misses.

**Options:** Train immediately; add a learned router; establish baseline and privacy tests first. **Selected approach:** I record the original detector and defer training while privacy/reproducibility gates are repaired. **Why selected:** It separates inherited faults from treatment effects. **Why not alternatives:** More models cannot repair storage isolation or measurement validity.

**Implementation:** scripts/probe_safety.mjs; docs/known_issues.md. **Verification:** Actual regex execution, build and lint. **Results:** Build succeeds; lint fails; diagnostic counterexamples reproduced. **Limitations:** Hand-selected labels are provisional and cannot estimate population safety. **Practical significance:** Prevents a polished UI or trained checkpoint being mistaken for validation. **Next step:** Privacy regression tests and reviewed curated replies.

## D003 — Same-prompt primary comparison, 2026-11-05

**Context:** Existing tuned_prompt and finetuned conditions change prompts as well as weights. **Evidence:** src/common.py and research README. **Options:** Compare their headline scores; factorial comparison; retain only A/B. **Selected approach:** I propose A=base/plain, B=base/tuned, C=adapted/tuned, with adapted/plain retained as a secondary factorial cell. **Why selected:** B/C isolates the inference-time effect of adaptation under the same prompt. **Why not alternatives:** An uncontrolled comparison cannot attribute a gain to LoRA.

**Implementation:** Protocol in first_milestone.md; runtime change pending. **Verification:** Planned exact message/config equality assertions. **Results:** No model comparison run. **Limitations:** Training prompt distribution and adaptation data still need specification; equal inference prompts alone do not control all confounds. **Practical significance:** Allows an interpretable treatment estimate. **Next step:** Freeze model revision, prompt and data manifest after development-only pilot.

## D004 — Candidate systems contribution, 2026-11-05

**Context:** LoRA, emotional-support datasets and model routing are established. **Evidence:** Literature matrix and actual device-tier selection code. **Options:** Claim a new empathetic chatbot; replicate methods; investigate measured browser routing costs. **Selected approach:** I propose measuring quality/safety jointly with model loading, switching, memory and latency costs. **Why selected:** Browser-local resource constraints may change which routing policy is worthwhile. **Why not alternatives:** Feature count and model use alone do not establish novelty.

**Implementation:** experiment_dependency_map.md and notebook_blueprint.md, proposed only. **Verification:** Fixed-small/fixed-large/rules comparisons with all switching overhead included. **Results:** No routing evidence. **Limitations:** This is a candidate gap, not proof that no prior work covers it. **Practical significance:** Could inform local model deployment beyond emotional support. **Next step:** Focused literature search and fixed-tier measurements before a learned router.
