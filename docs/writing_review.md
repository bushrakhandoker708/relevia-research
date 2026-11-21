# Writing review and remaining verification

Date: 5 November 2026. Scope: the Relevia application and Relevia research repositories, as confirmed by Bushra. This review applies the supplied writing policy; it does not convert proposed experiments into completed work.

## What changed and why

I want the project descriptions to explain what Relevia is investigating, why its implementation choices matter and what the evidence can support. Both READMEs now follow that progression. They distinguish the prototype’s intended purpose from measured outcomes, explain the storage compromise and identify incomplete research. They also disclose agent assistance rather than implying independent personal implementation or testing.

A writing guide and agent instructions were also added at this point. They were later removed from both repositories and are kept privately.

The active protocol, plan, prompt log, rating guide, deployment guidance and notebook Markdown were reviewed. The review corrected validation-based prompt-development instructions, unsupported deployment thresholds and unmeasured runtime or model-quality claims. Existing audit documents retain their historical findings with a reading-context note pointing to Milestone 2. Historical decision entries and experimental evidence have not been rewritten to hide failures.

The three notebooks explain the intended comparisons, controls and limitations while keeping outputs empty. The results notebook now explicitly distinguishes a commented analysis sketch from implemented agreement and uncertainty calculations. The training scaffold explains the adaptation hypothesis and low-rank update without claiming that lower training cost establishes better dialogue. The Colab scaffold identifies its older condition loops as incompatible with treating the tuned B/C comparison as already implemented there.

Code-header corrections in `data/build_dataset.py`, `src/train.py`, `src/generate.py` and `src/evaluate.py` remove unsupported guarantees and clarify methodological intent. Abstract syntax trees were compared immediately before and after those edits and were identical. No algorithm changed in this writing pass. Conventional utility comments are retained where they already explain the implementation clearly.

## Evidence and limits

Both repositories pass `git diff --check`. Notebook JSON parses and all recorded outputs remain empty. Local document links were checked in the earlier pass; the final review repeats that check across the complete Markdown inventory. The writing pass does not claim a new production build or model run. The existing Milestone 2 verification remains the implementation evidence.

A Windows browser retry was stopped by the computer-use tool because URL-policy enforcement is unsupported for the current browser. No successful privacy interaction check followed. The owned local Vite server was stopped in the subsequent turn. This is an environment limitation, not a browser-test pass.

A metadata-only inspection of `archive/v1_original/empathy_42k.jsonl` found 15,000 valid JSON rows. Every row has `prompt` and `response` fields, with no row-level source identifiers. SHA-256: `a78dac24c48e4b14282de4f7293f54f5984a06dc56f717dd4b317dda7cab6891`. No email or HTTP URL pattern was found. These narrow checks cannot detect names, private narratives, all identifiers or licence violations. The archive’s existing description of faulty pairing remains an unreplicated historical account, and the artifact is not cleared for redistribution.

The earlier application health-information copy still requires a separate evidence-based content review, as already identified in the audit. Rewriting the project’s purpose does not validate absolute reassurances inside those pages. No clinical benefit or universal privacy claim follows from this documentation work.

## Completion boundary

The writing convention is persistent within both repositories and the main descriptions, supporting documentation and notebook narratives have been revised. The combined request also resumes Milestone 2. Its browser gap and archived-data provenance remain unresolved, and no training, publication or Milestone 3 work is authorised by this review. On 5 November 2026, Bushra explicitly accepted the missing browser verification as an exception for local research work only. This records a scope-limited acceptance, not a successful browser test. Browser interaction, lifecycle, legacy IndexedDB and multi-tab checks remain required before release. The acceptance does not clear the archived dataset’s provenance or authorise its redistribution, model training, deployment or a public push. The next unresolved decision concerns provenance evidence or an agreed disposition for the historical dataset before public redistribution.
