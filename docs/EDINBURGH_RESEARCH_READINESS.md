# Edinburgh research readiness — 7 November 2026

## Research summary

I want to investigate how supportive response quality, safety and computational cost interact in small local language models. Relevia provides an application testbed and a separate research repository. The current work fixes privacy and safety defects, quarantines an unresolved historical dataset, compares two frozen prompts on the same pinned Qwen2.5-1.5B model, and records inference costs separately from quality. An eight-scenario pilot is inconclusive; a 60-scenario extension generated 120 responses but has no independent human ratings. The strongest current contribution is reproducible experimental groundwork and an explicit account of failures, rather than a demonstrated improvement from prompting or adaptation.

## Specific systems question and evidence

For a fixed small model and device, how do prompting and later parameter-efficient adaptation change the joint distribution of grounded supportive quality, harmful-response outcomes, startup cost and generation latency? A future routing study should include loading and switching overhead rather than assuming a larger model is free once selected. This connects the project to the CDT's emphasis on ML methods and the systems that implement them. [Programme description](https://informatics.ed.ac.uk/cdt-in-machine-learning-systems)

The inspectable evidence includes session-only default chat storage, opt-in persistence and deletion tests; conversation-group leakage checks; hash-frozen model, prompt and input configuration; raw A/B generations; separate routing confusion matrices; paired-analysis code; and executed notebooks. Work was coding-agent-assisted. Bushra should be able to explain and reproduce the methods herself before using this as evidence of personal competence.

## Completed experiments and negative findings

The original eight-scenario pilot generated 16 responses. Unblinded agent ratings gave relevance B−A = +0.125 with a 95% bootstrap interval of −0.875 to +1.125. This does not establish improvement or equivalence. Both conditions retained an urgent-response failure.

The extension generated all 120 responses on 60 new synthetic scenarios without runtime failure. A hit the 110-token limit 30 times and B once. Twenty-four B responses exceeded its requested 65-word limit. These observations describe execution and instruction compliance, not empathetic quality. Independent human ratings and agreement remain missing.

The frozen routing comparison gave S1 11 true positives, three false negatives, 16 true negatives and zero false positives on the labelled held-out cases. The labels are provisional and agent-authored. S1 recall is 0.786 with a wide Wilson interval of 0.524–0.924. It still misses indirect, obfuscated and French risk language.

Five repeated generations per condition on the original timing-outlier input took 21.7–32.5 seconds for A and 16.3–25.5 seconds for B. The original 527.9-second delay did not recur and remains unexplained. A new 956.7-second observation overlaps a recorded Windows Modern Standby interval, exposing a host-availability confound. Python float32 timings are not WebLLM browser measurements.

## Skills demonstrated and limits

The artifacts demonstrate attention to experimental controls, data leakage, provenance, regression testing, paired inference, uncertainty, ordinal annotation and runtime instrumentation. These are concrete topics for discussion. The current evidence does not demonstrate a novel adaptation algorithm, independently validated response quality, robust multilingual safety, clinical benefit, energy efficiency or a browser benchmark. Agent-written code and prose require author review and accurate assistance disclosure.

The project is suitable for a **preliminary supervisor discussion**, provided its limitations are stated. It is not yet a defensible claim that developed prompting improves supportive quality or that LoRA is ready for evaluation. Research originality still requires a fuller related-work comparison and a sharper hypothesis about the quality–cost–safety trade-off.

## Proposed next investigation and supervisor questions

Obtain two independent blinded reviews of a feasible ordinary-context subset before deciding whether to adapt the model. Then compare B with an adapter on the same base model and same prompt, with unchanged final test inputs and separate safety outcomes. Ask a prospective supervisor:

- Is this a useful empirical ML-systems question, and which deployment constraint would make it distinctive?
- What annotation design, sample size and ethics process would make supportive-quality claims credible?
- Should the next controlled intervention be LoRA, quantisation or runtime/backend choice?
- How should host suspension, caching and device variability enter the performance protocol?
- What level of safety coverage is needed before involving participants or demonstrating a public application?

The brief can support an initial conversation now; a completed LoRA model is not needed to explain the question and existing evidence. No supervisor has been contacted by the agent.

## Application work that remains outside this repository

The official Round 1 first-stage deadline is **14 December 2026, 23:59**; this round accepts international applicants. Round 2 is Home-only. Selected first-stage applicants are invited to the full application stage. Verify the form and current deadlines again before submission. [Official deadlines](https://informatics.ed.ac.uk/cdt-in-machine-learning-systems/apply/application-process-and-guidance/application-deadlines)

The normal academic minimum is a relevant UK 2:1 honours degree or international equivalent; a master's degree is not mandatory. English-language evidence and, where applicable, ATAS requirements also need checking. Eligibility cannot be inferred from the project. [Official eligibility requirements](https://informatics.ed.ac.uk/cdt-in-machine-learning-systems/apply/eligibility-and-entry-requirements)

Bushra still needs to confirm degree equivalence, current grades, expected graduation and availability for the programme; obtain transcripts; identify referees and check the required number and submission dates; check English-language evidence and its validity; and prepare the current first-stage form, CV and research-interest explanation. These personal details were not supplied or verified here. Use the official [application process](https://informatics.ed.ac.uk/cdt-in-machine-learning-systems/apply/application-process-and-guidance). The detailed guidance page returned HTTP 403 during this check, so reference counts and form-specific requirements are deliberately not asserted.

Protect the application deadline from an open-ended implementation schedule. Prepare a concise, accurately qualified research summary for relevant prospective supervisors while the evaluation continues. No project score, benchmark result or supervisor contact guarantees admission.
