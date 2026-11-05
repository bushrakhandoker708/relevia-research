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


## D005–D009 implementation follow-up — 2026-11-05

**Context and evidence:** Milestone 2 reproduced shared persistence and four overlapping few-shot conversation groups. The app and research repositories were clean at d6d2ec2f8ccbeb69b0b992bb24b64af52fed68ce and 5c9c051a09b107644e7984a4609ecae64b8becef respectively. Both now use research/privacy-foundation branches.

**Options and selected approach:** Memory-first sessions with opt-in bounded snapshots were selected over authentication or retaining shared IndexedDB defaults. Explicit reopening avoids automatic cross-session context. Epoch invalidation was added because deleting disk records alone permits pending generation to restore them. The Home letter no longer consumes chat history. See privacy_design_decisions.md for the full decision-by-decision rationale and alternatives.

**Implementation:** chatStorage.js, db.js, ChatPrivacy.jsx, Chatbot.jsx, releviaBrain.js and the privacy-related service changes in the app; splits.py, build_dataset.py and the harness in the research repo. Formerly exposed validation groups are quarantined rather than relabeled as pristine. Official test bytes are preserved. The A/B harness rejects unpinned revisions and unsupported adapted conditions.

**Verification and results:** 18 JavaScript tests and eight Python tests pass; changed-file lint passes; production build passes. Group overlap is zero across all 15 split pairs. Full legacy lint remains failing. Reachable-history/current-bundle scans found no selected credential patterns or exact local .env values. No model ran and no scores were generated.

**Limitations and practical significance:** These changes reduce automatic retention and remove a concrete evaluation leak; they do not prove clinical safety or shared-device access control. Browser verification timed out, and the already-tracked historical dataset still needs provenance/privacy review. The first CLI integration test failed due to host temporary-directory permissions; using a verified workspace temporary directory resolved it. Initial inconsistent dataset reads motivated atomic file replacement and hashing the bytes actually parsed.

**Next step:** Complete the disposable-profile browser checklist and resolve/accept the archival-data exception before Milestone 3. Do not silently overwrite this entry if later tests contradict it.


## Writing and protocol consistency review — 5 November 2026

Bushra requested that both Relevia repositories use her supplied writing policy. Each repository now contains a writing guide and persistent agent instructions. The application and research descriptions explain purpose, constraints, implemented behaviour and evidence without attributing agent-performed implementation or tests to independent personal work.

The documentation review exposed methodological contradictions rather than only stylistic differences. The older plan and prompt log still directed prompt development towards validation data, although Milestone 2 now reserves development conversations. Those instructions were corrected. The notebook’s suggestion that 25 wins out of 40 justified deployment was withdrawn because it was not an established safety or release threshold. Unmeasured runtime estimates and unsupported claims of model quality were removed from the notebook introduction.

Historical literature notes retain their original claims with an explicit verification-status correction; they must not be cited as a completed full-text review. The archived deployment procedure is now labelled unverified and deferred. Earlier audit and decision entries remain historical records rather than being rewritten to imply later fixes existed at the time.

This review changed prose and notebook Markdown, not model outputs. All three notebooks parse as JSON and contain no recorded outputs. Both repositories pass git diff --check. The earlier automated test evidence remains the evidence for implementation; documentation edits do not constitute a new test run. Browser verification and archival-data review remain unresolved, so no milestone sign-off or permission to begin training follows from this writing revision.


## Browser exception accepted for local research — 5 November 2026

On 5 November 2026, Bushra explicitly accepted the missing browser verification as an exception for local research work only. This records a scope-limited acceptance, not a successful browser test. Browser interaction, lifecycle, legacy IndexedDB and multi-tab checks remain required before release. The acceptance does not clear the archived dataset’s provenance or authorise its redistribution, model training, deployment or a public push.
