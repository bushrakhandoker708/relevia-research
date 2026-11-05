# Research plan

I want the model comparison to answer a specific question: does adaptation improve supportive dialogue beyond a developed prompt under the constraints of the Relevia application? Before spending compute on that comparison, the storage boundaries and evaluation data need to support an interpretable experiment.

Milestone 2 addresses those prerequisites. Its automated checks pass in the recorded environment, but browser verification and the archived dataset review remain open. No training, model routing or deployment should begin until the milestone is accepted. The older schedule and compute estimates were planning assumptions, not measured feasibility results; they must not be used as a promise about completion time or cost.

The next investigation is the A/B prompting pilot in [Experiment 01](experiment_01_protocol.md). Development data are the only source for prompt changes. Validation supports model selection; the final test sets remain isolated. The earlier instruction to tune prompts on validation was a methodological error and has been superseded by the [leakage repair](dataset_leakage_report.md).

After the foundation is accepted, the proposed sequence is to verify an immutable model revision and its licence, review the prompts and synthetic scenarios, prepare a manifest, and run the controlled baseline. This first run should measure feasibility and expose pipeline failures. It cannot establish general dialogue quality from four instrumentation scenarios.

A later comparison may add adaptation using the same inference prompt as condition B. Before that work, record the training configuration, resource budget, repeated-seed plan and selection rules. Review the expanded benchmark and rating procedure, including any institutional requirements for human participation. Freeze the primary analysis before inspecting final test outcomes.

Browser deployment is a separate stage. It requires a verified conversion path and measurements of loading, generation and memory on identified devices. Faster or smaller models are not necessarily safer or more helpful. The final report should connect quality, safety and deployment evidence while retaining failures and uncertainty.

The older four-model, three-seed programme remains a possible expansion, not the current execution plan. A measured pilot should determine whether its compute and review workload are realistic. No calendar commitment or numerical runtime estimate has yet been established by this milestone.
