# Initial literature synthesis and reading plan

Inspected 5 November 2026. **Status: initial gap analysis, not a completed systematic review.** Primary paper landing pages/abstracts were checked for the requested references; selected full-text pages were inspected for RouteLLM, judge evaluation and the closely related PTSD study. Numerical claims in older local notes have not all been reconciled with full tables. Do not describe every paper as fully read or reproduced.

## Critical synthesis

Parameter-efficient adaptation, supportive-dialogue datasets and model routing are established methods. Combining them in a chatbot is not itself algorithmic novelty. A defensible candidate contribution is a controlled study of how adaptation and browser resource limits jointly change supportive quality, harmful responses and selective-inference cost. This is a proposed empirical contribution; a wider related-work search is still required before claiming an uncovered gap.

[LoRA](https://arxiv.org/abs/2106.09685v2) represents a weight update as a low-rank product while freezing the original weights. [QLoRA](https://arxiv.org/abs/2305.14314v1) reduces training memory through quantized frozen weights and trainable adapters. Neither method implies safer support responses or improvement over a well-optimized prompt. Their role here is to make the treatment affordable, not establish the treatment's value. Start with the existing 1B configuration; choose ordinary LoRA if supported memory makes QLoRA complexity unnecessary.

[EmpatheticDialogues](https://aclanthology.org/P19-1534/) motivates emotional acknowledgment, whereas [ESConv](https://aclanthology.org/2021.acl-long.269/) adds support-strategy structure. These are related but different objectives. A reply that sounds understanding can still agree with a false premise or give inappropriate reassurance. Source-specific evaluation is preferable to blindly pooling datasets and interpreting a single average as safety.

[XSTest](https://aclanthology.org/2024.naacl-long.301/) is particularly relevant to the observed regex false alarms: safety-associated words can occur in benign requests. Its contrastive testing idea should be adapted to negation, quotations and educational contexts, while separately testing indirect urgent language. This does not make Relevia's new fixtures an XSTest replication or a validated clinical benchmark.

[HELM](https://arxiv.org/abs/2211.09110v2) motivates multidimensional evaluation. [Zheng et al.](https://arxiv.org/abs/2306.05685v4) identify position, verbosity and self-enhancement biases in automated judging. Therefore human-rated quality, safety outcomes and system cost remain separate. A judge can assist annotation only after comparison with blinded human ratings; an automated preference score is not a clinical safety label.

[FrugalGPT](https://arxiv.org/abs/2305.05176v1) and [RouteLLM](https://arxiv.org/abs/2406.18665v4) establish cost-aware cascades and preference-based routing. Relevia should test whether their motivation transfers to local browser deployment, where loading a stronger model may cost more than the request it improves. A fixed model can win once download, cache, switching and memory pressure are included. The non-generative urgent-support path introduces a different action and evaluation criterion; it is not simply a “stronger model” preference decision.

[StreamingLLM](https://arxiv.org/abs/2309.17453v4) studies attention-sink-based streaming. Relevia's stepped history window is not an implementation of that algorithm. Short supportive chats provide no immediate justification for integrating long-context machinery. Measure prompt truncation and cache behavior first.

## Closest related studies already cited locally

[Suhas BN, Yash Mahajan, Dominik Mattioli, Andrew M. Sherrill, Rosa I. Arriaga, Chris W. Wiese and Saeed Abdullah (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1573.pdf), *The Pursuit of Empathy: Evaluating Small Language Models for PTSD Dialogue Support*, directly overlaps small-model supportive generation. Its abstract describes eight small models and a 10,000-dialogue synthetic dataset, with adaptation gains varying by scenario. Existing local notes summarize fine-tuning as not clearly better; that stronger interpretation must be reconciled with the paper's detailed tables rather than treated as settled. Relevia should distinguish its tuned-prompt control and browser systems investigation, not claim to originate small empathetic models.

[Lujain Ibrahim, Franziska Sofia Hafner and Luc Rocher (Nature, 2026)](https://doi.org/10.1038/s41586-026-10410-0), *Training language models to be warm can reduce accuracy and increase sycophancy*, is directly relevant to warmth versus correctness. Publisher search material confirms the paper and intervention; full publisher access failed in this session. Exact effect sizes and model-specific applicability remain to verify. This supports measuring harmful agreement separately, not predicting that Relevia's adapter will necessarily worsen it.

## Literature matrix

| Paper / source | Problem | Method | Data | Metrics | Limitations | Relevia decision | Implementation status |
|---|---|---|---|---|---|---|---|
| Hu et al., LoRA, 2021 arXiv v2 | Adaptation cost | Frozen W plus low-rank BA | Multiple model/task experiments | Task quality, parameters, memory | Original scales/tasks differ | Rank ablation only after baseline | Existing LoRA script; no current run evidence |
| Dettmers, Pagnoni, Holtzman, Zettlemoyer, QLoRA, 2023 | Training memory | NF4, double quantization, paged optimizers | Instruction tuning across models/datasets | Quality, memory, human/judge comparisons | CUDA training is not browser quantization | Verify GPU compatibility; keep export separate | Existing NF4 script; unexecuted here |
| Rashkin, Smith, Li, Boureau, ACL 2019 | Empathetic dialogue data | Emotion-grounded dialogue benchmark | EmpatheticDialogues | Human/automatic response evaluation | Empathy is not urgent-risk competence | Source-aware splits and data card | Local preprocessing/data present |
| Liu, Zheng, Demasi, Sabour, Li, Yu, Jiang, Huang, ACL-IJCNLP 2021 | Support strategies | ESC framework and annotated conversations | ESConv | Support-strategy/dialogue evaluation | Crowdsourced support is not clinical validation | Separate candidate source/strategy analysis | Not integrated |
| Liang et al., HELM, arXiv 2022/2023 v2 | Narrow evaluation | Standardized multi-scenario metrics | Many scenarios/tasks | Multiple quality/risk/efficiency dimensions | Coverage cannot establish universal reliability | Report separate outcomes | Proposed |
| Röttger, Kirk, Vidgen, Attanasio, Bianchi, Hovy, NAACL 2024 | Excessive refusal | Contrastive safe/unsafe test suite | XSTest | Compliance/refusal outcomes | Not a mental-health diagnostic test | Benign lexical controls | Diagnostic probes only |
| Zheng et al., NeurIPS Datasets and Benchmarks 2023 | Scalable judging | MT-Bench/Arena and judge-human comparisons | Multi-turn questions/preferences | Agreement, preferences, bias | Style and order influence scores | Human calibration and blinded identity | Rating-sheet script exists; no completed ratings |
| Chen, Zaharia, Zou, FrugalGPT, arXiv 2023 | API cost | Learned model cascade | Query benchmarks | Cost and task performance | API economics differ from local GPU costs | Include all route overhead | Proposed |
| Ong, Almahairi, Wu, Chiang, Wu, Gonzalez, Kadous, Stoica, RouteLLM, arXiv v4 2025 | Strong/weak model allocation | Preference-trained routers | Arena preferences and benchmark evaluations | Quality-cost trade-off | Preference transfer is not risk calibration | Rules before learned routing | Not implemented |
| Xiao, Tian, Chen, Han, Lewis, StreamingLLM, arXiv v4 2024 | Streaming context | Retain attention sinks plus recent tokens | Streaming language-model evaluation | Perplexity and efficiency | Different algorithm from cropping messages | Defer until long-context need measured | Not implemented |
| NIST AI 600-1, July 2024 | Generative-AI risk | Risk-management profile | Guidance, not a training corpus | Process/evaluation guidance | Not certification | Explicit release evidence | Initial threat model |
| WHO, January 2024 LMM guidance | Health-related AI governance | Ethical/governance recommendations | Guidance | No Relevia performance measure | Guidance is not outcome validation | Non-clinical scope and research review | Proposed release gates |
| WebLLM documentation, observed 0.2.87 | Browser inference | WebGPU runtime and workers | Model/runtime artifacts | Implementation-specific | Current docs differ from locked 0.2.79 | Verify against installed version | App builds; live inference untested |

References for the last three rows: [NIST](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), [WHO](https://www.who.int/news/item/18-01-2024-who-releases-ai-ethics-and-governance-guidance-for-large-multi-modal-models), [WebLLM](https://webllm.mlc.ai/docs/). Exact full-author/venue bibliographic exports for long-author papers remain to complete before submission.

## Data licensing and reuse gate

The [EmpatheticDialogues license](https://github.com/facebookresearch/EmpatheticDialogues/blob/main/LICENSE) is CC BY-NC 4.0. The [ESConv license](https://raw.githubusercontent.com/thu-coai/Emotional-Support-Conversation/main/LICENSE) is also CC BY-NC 4.0, while its [repository README](https://github.com/thu-coai/Emotional-Support-Conversation) says data/code are for academic research use only. Do not infer unrestricted public/commercial model distribution from download access. Record the precise dataset release, attribution, license text and intended research use; resolve deployment permissions before publishing adapted weights. No new dataset was downloaded or redistributed in this milestone. Paper availability and code availability do not independently authorize all data uses.

## Reading work still required

MUST: complete full-text extraction for LoRA, QLoRA, ED, ESConv, XSTest and the two closest supportive/warmth studies. For each, record full citation/venue/version; research question; algorithm and assumptions; data/training procedure; metrics; numerical findings with table/page and denominator; limitations; code/data license and pinned release; Relevia decision; alternative rejected; implementation status; replication versus novelty.

TARGET: RouteLLM, FrugalGPT, HELM and judge evaluation in depth; trace their baselines and contamination controls. STRETCH: StreamingLLM implementation only if profiling reveals a relevant context bottleneck. Avoid an unbounded reading programme before coursework.

Maintain three separate labels in notes: **paper evidence**, **Relevia hypothesis**, and **engineering preference**. Presently, browser switching overhead as a decisive factor is a hypothesis; preserving existing workers is an engineering preference supported by architecture, not a measured performance finding.


## Milestone 3 source verification

The official EmpatheticDialogues and ESConv licence files were checked on 5 November 2026: both are CC BY-NC 4.0, and ESConv’s README additionally states academic-research-only use. The earlier archive’s MIT label is incorrect. Rashkin et al. motivate emotional context; Liu et al. motivate support strategies. Neither dataset establishes clinical safety. The initial pilot therefore uses new synthetic text with explicit agent-review limits rather than pooling these corpora.

The [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) and [pinned licence](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/989aa7980e4cf806f80c7fef2b1adb7bc71aa306/LICENSE) support the model identity and Apache-2.0 terms. Its selection reflects access and CPU feasibility, not clinical suitability. [LoRA](https://arxiv.org/abs/2106.09685v2) reduces trainable parameters, but a controlled prompting baseline is needed before attributing any benefit to adaptation. The [Pursuit of Empathy abstract](https://aclanthology.org/2025.emnlp-main.1573/) reports variable fine-tuning gains; the older blanket conclusion that fine-tuning was not better remains unsuitable as a settled literature claim. No new full-paper replication is claimed.
