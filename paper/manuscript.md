# Prompting, adaptation and safety routing for small local language models in supportive dialogue: a controlled groundwork study

*Working draft, 8 November 2026. Author: Bushra Khandoker. Drafted with coding-agent assistance for the author's review; see §10.3. This is not a submitted paper. It contains no novelty claim and no quality result, because the independent ratings that would support one do not yet exist.*

## Abstract

Small language models that run on a user's own device are attractive for supportive conversation, because a sensitive message never has to leave the device. They are also weak. Whether the better route to an acceptable reply is careful prompting or parameter-efficient adaptation is an empirical question, and the answer must account for safety and runtime cost as well as reply quality. This draft describes the controlled groundwork built to ask that question on one pinned model, Qwen2.5-1.5B-Instruct. It covers conversation-level data separation, a frozen two-prompt comparison (A and B) on 60 new synthetic scenarios, a three-version deterministic safety router (S0, S1, S2) evaluated on frozen held-out sets, and a LoRA pipeline that has passed a four-step CPU smoke test. The execution results are reproducible. Prompt B wrote shorter replies (median 19 tokens fewer per pair) and reached the 110-token cap in 1 of 60 replies against 30 of 60 for A. It cost about 2.4 s more before the first token and about 0.05 s more per generated token. The normalised router S2 detected 18 of 24 agent-labelled urgent messages (recall 0.75, 95% Wilson interval 0.55–0.88), compared with 9 of 24 for its predecessor, with no false alarms on 18 non-urgent messages. None of these results says whether a reply was more supportive. That question waits for blinded independent ratings, of which there are currently none.

## 1. Introduction

A person who writes "i wanna die tbh" to a supportive chatbot needs two things from it. First, the system must notice. Second, the reply must neither dismiss them, refuse to engage, nor invent a phone number. A small model running in a browser makes the privacy argument easy and both of those requirements harder. The question that motivated this work is practical: for a fixed small model, is it better to spend effort on the prompt or on adapting the weights, and what does each choice cost in safety and speed?

The project began as an application, Relevia, and became a research project when it was clear that the application could not answer that question honestly. The application stored history across sessions, its privacy wording overstated what it did, and the research pipeline reused validation conversations as prompting examples. Those defects had to be fixed before any comparison between conditions could mean anything. Much of the work reported here is therefore groundwork. It still produced measurable results, but mostly about execution, routing and cost rather than quality.

## 2. Problem

Three properties have to be measured together, because improving one can damage another.

- **Supportive quality.** Does the reply recognise the feeling, stay relevant and avoid stock phrasing? This needs human judgement. Lexical proxies are not a substitute.
- **Safety.** Are urgent messages routed to a fixed safe response? Does the generated reply avoid refusal, false reassurance, invented contact details and encouraging dependency?
- **Cost.** How long do startup, time to first token and generation take on the hardware a user actually has?

Training language models to be warmer has been reported to make them less accurate and more likely to agree with incorrect user beliefs, especially when the user expressed sadness (Ibrahim, Hafner and Rocher, 2026, *Nature*; preprint arXiv:2507.21919). The bibliographic record and the preprint abstract have been checked, but not the publisher's full text. Its smallest model has 8B parameters. Whether a comparable trade-off appears at 1–2B parameters, and whether it differs between prompting and adaptation, has not been tested here or, as far as the incomplete literature review shows, elsewhere. That last point is a reading gap, not a novelty claim.

## 3. Research questions

- **RQ1 (quality).** On the same pinned base model and the same inference prompt, does a LoRA adapter (C) improve blinded ratings of supportive quality over the developed prompt alone (B)?
- **RQ2 (safety).** Does C change the rate of generative safety failures (refusal, invented contacts, false reassurance, dependency language, unsupported medical claims) relative to B? Separately, how much of the urgent-message risk does deterministic routing remove before generation?
- **RQ3 (cost).** What do B and C cost in startup, time to first token, prefill and decode throughput, and failure rate, in Python on CPU and later in the browser on WebGPU?

The B–C comparison is the principal one. A versus B describes prompt development. It is already partly measured, but it is not an answer to RQ1.

## 4. Related work

*Status: partial. On 8 November 2026 the bibliographic details of every cited work were checked against arXiv or the publisher (see `references.bib`). Claims about content come from abstracts only, unless stated otherwise.*

**Parameter-efficient adaptation.** LoRA freezes the pretrained weights and learns a low-rank update to selected projection matrices (Hu et al., 2021). QLoRA keeps the frozen base in 4-bit precision while training the adapter (Dettmers et al., 2023). This study uses ordinary LoRA first, so that quantisation is not a second treatment in the B–C comparison.

**Empathetic dialogue data and measurement.** EmpatheticDialogues provides about 25,000 crowd-sourced conversations grounded in 32 emotion labels (Rashkin et al., 2019). EPITOME splits empathy into emotional reactions, interpretations and explorations (Sharma et al., 2020); the rating rubric in `docs/rating_guide.md` is adapted from it. ESConv frames emotional support as a strategy sequence (Liu et al., 2021) and is a candidate for future multi-turn evaluation.

**Small models for supportive dialogue.** BN et al. (2025, EMNLP; arXiv:2505.15065) evaluated eight small models (0.5–5B) on a synthetic PTSD dialogue set, zero-shot and after fine-tuning. Their abstract reports that fine-tuning *improved* similarity to reference replies and perceived empathy, with gains that varied across scenarios and a "knowledge transfer ceiling" for the smallest models. **Correction (8 November 2026):** the project's earlier literature notes said this paper found fine-tuning "not clearly better". That reading contradicts the abstract and has been withdrawn until the full text is checked. This is the closest prior work found so far, and it makes a B versus C comparison on a 1.5B model a reasonable question rather than an expected null result.

**On-device support models.** EmoSApp (A et al., 2025, IJCNLP-AACL; arXiv:2507.10580) fine-tuned and quantised Llama-3.2-1B-Instruct, which is also Relevia's default browser model. It ran on Android phones fully offline and was evaluated with students and mental-health professionals and on reasoning benchmarks. This is closer to Relevia than BN et al. It means that a small, quantised, on-device support model is not itself a contribution here. Its abstract does not report crisis routing or browser deployment, and no other safety measurement is described.

**Quantisation and safety.** Kharinaev et al. (2025, arXiv:2502.15799) compared 66 quantised variants of four models and report that both post-training and quantisation-aware methods can degrade safety alignment. Their safety questions are general rather than about supportive dialogue. They do not change the inference runtime, which in Relevia's case also differs between the evaluated configuration (PyTorch on a CPU) and the deployed one (MLC on WebGPU). Both papers are cited from their abstracts only.

**On-device inference.** WebLLM runs quantised models in the browser on WebGPU (Ruan et al., 2024). The base model's report is Qwen Team (2024).

**Still to read before any positioning claim:** Qian et al. (2023), Loh and Raamkumar (2023), Filienko et al. (2024), Park et al. (2024) and Lee et al. (2023). These are listed in the literature notes and are not cited as evidence here.

## 5. Contribution (as currently supported)

What the evidence supports today:

1. A conversation-separated data pipeline with zero group overlap across all 15 partition pairs, hash-frozen inputs and a quarantined historical archive.
2. A controlled A/B execution record (120 generations, no runtime failures) with paired re-analysis showing that an apparent latency advantage for B is a length effect plus a host-suspension confound.
3. Three versions of a deterministic safety router, each evaluated on a set frozen before that version was written, with frozen detector copies so that old results still reproduce.
4. A LoRA pipeline for the B–C comparison that changes only the adapter, refuses the final test set and has passed a smoke test.
5. Browser benchmark instrumentation that separates cold and cached startup, runtime-reported prefill and decode rates, failures and unloading, with one executed run on this laptop's integrated GPU.
6. S3, a tiered input router with a non-generative emergency path, evaluated once on a set frozen before it was written and checked for over-routing on unseen human-written text.

What is not supported: any claim that B or C is more supportive, any clinical claim, any browser result beyond one laptop's integrated GPU, and any novelty claim.

## 6. System architecture

The application is a React client. A Web Worker hosts WebLLM 0.2.79, which runs a quantised Llama-3.2 or Qwen2.5 model on WebGPU. Each user message passes through three stages:

1. **Route.** `src/services/safetyS3.js` (S3, since 8 November 2026) classifies the message as `emergency`, `urgent`, `check_in` or `none`. Something already taken or done, or the means in hand with intent, receives a fixed emergency-services message. Other urgent messages receive a fixed support message. Neither is ever generated. S2 (`safety.js`) is kept unchanged for comparison.
2. **Generate.** Otherwise the model streams a reply under the application's system prompt.
3. **Guard.** `src/services/replyGuard.js` (G2) checks the reply as it streams. Only checked sentences are shown, plus the unfinished one when nothing in it could still become a refusal or a contact detail. An inappropriate refusal is replaced with a fixed message. A legitimate one, such as declining to give overdose information, is kept. A sentence containing an unverifiable named service or phone number is removed, and the one verified line is added. The first version (G1) was added after a logged reply refused to discuss a death and gave an outdated United States hotline number. G2 followed an audit showing that G1 could display part of a problem before catching it.

Conversation history is session-only by default. Persistence requires explicit consent and can be deleted. The research repository mirrors the generation path in Python (`scripts/generate_bc.py`) so that B and C can be compared under controlled settings. The Python path is not claimed to be numerically equivalent to the browser path.

## 7. Dataset methodology

Training and validation data come from the official EmpatheticDialogues release, licensed CC BY-NC 4.0. An earlier archive note claiming an MIT licence was wrong and has been corrected (`docs/dataset_provenance_report.md`). Conversations are split by conversation group into train, development, few-shot, validation and test partitions. `scripts/check_leakage.py` confirms zero group overlap and zero normalised-pair overlap across all pairs. A 15,000-row historical archive of uncertain provenance is quarantined with its hash recorded and is excluded from every active path.

The prompt comparison uses synthetic scenarios: an eight-scenario pilot and a 60-scenario extension across six everyday categories. The extension has no group or input overlap with development, and its token-Jaccard near-duplicate check (threshold 0.65) found nothing. The safety sets (v2 and v3) are synthetic, agent-authored and frozen with SHA-256 hashes before the detector version they evaluate was written. Their labels are provisional, and the agent that wrote v3 also wrote S2, so that evaluation is not independent.

The LoRA pilot selects whole conversation groups with a seeded procedure. The smoke test used 16 training rows from 9 groups and 8 validation rows from 4 groups, with the selected IDs hashed in the manifest. The final 60-case test set is never read by the training script.

## 8. Experimental design

**Conditions.** A: minimal safe prompt. B: developed prompt `B-dev-revision-2`, frozen after two development rounds that used development data only. C: B plus a LoRA adapter on the same pinned base `Qwen/Qwen2.5-1.5B-Instruct` at revision `989aa79…`. Decoding is identical across conditions: greedy, at most 110 new tokens, seed 42, CPU float32 with eight threads.

**Adapter (pre-registered, not tuned).** Rank 8, alpha 16, dropout 0.05, targets `q_proj` and `v_proj` (1,089,536 trainable parameters, 0.07% of 1.54B). Loss is computed on assistant tokens only, prompt B is the system message, the maximum length is 512, gradient accumulation is 8 and the learning-rate candidates are 1e-4 and 2e-4. A learning rate is selected on validation loss plus a development safety review, never on the final test set.

**Smoke test (run).** Four optimiser steps on CPU. Validation loss on 7 usable validation examples went from 4.020 to 3.665 in 176.5 s, the process peaked at 7.25 GB RSS and the adapter took 4.4 MB. The test shows that the pipeline runs end to end: masking, template alignment, saving and the manifest. It is not evidence of learning, because 4 steps on 15 examples are far too few and the validation subset is tiny.

**Pilot (not run).** Up to 256 training rows, requiring the author's recorded approval and preferably a CUDA GPU. The development machine has an RTX 4060, but the installed PyTorch is a CPU build.

**Safety evaluation.** Routing is measured with precision and recall against frozen labels, using Wilson intervals and paired McNemar tests between detector versions. The generated replies to the same held-out messages are scanned for lexical failure flags. This separates two failure types: the router missing an urgent message, and the model writing something harmful once it is allowed to generate.

**Quality evaluation (blocked).** Two blinded independent reviewers rate each reply on an EPITOME-derived rubric with a separate hazard judgement. The rating sheets exist; 0 of 120 items are rated.

## 9. Metrics and current results

| Measure | Result | Status |
|---|---|---|
| A vs B token-cap hits (60 pairs) | A 30/60, B 1/60; McNemar exact p = 3.7e-9 | Execution fact |
| B − A output tokens | median −19 per pair | Execution fact |
| B − A time to first token | median +2.4 s; B slower in 57 of 58 pairs | Execution fact, CPU |
| B − A time per generated token | median +0.050 s; B slower in 54 of 58 | Execution fact, CPU |
| B − A end-to-end latency, standby pairs excluded | median −3.3 s (B sooner), sign test p = 0.087 | Explained by B's shorter replies |
| Router recall on v3 (24 urgent) | S0 13/24, S1 9/24, S2 18/24 (0.75, 0.55–0.88) | Agent labels, not independent |
| Router false-positive rate on v3 (18 non-urgent) | S0 3/18, S1 0/18, S2 0/18 | Agent labels |
| LoRA smoke validation loss | 4.020 → 3.665 after 4 steps | Pipeline check only |
| Generative safety flags on v3 (B, 45 replies) | 0 refusals, 0 reassurance/dependency/medical flags, 1 contact flag (false positive) | Lexical flags, not ratings |
| Replies to the 6 urgent messages S2 misses | 4 of 6 read as harmful or inadequate (e.g. no emergency direction after a stated overdose); none flagged | Agent reading, not ratings (`docs/safety_failure_taxonomy.md`) |
| Router recall on v4 (46 urgent incl. 13 emergencies), first run | S2 13/46 (0.28); S3 43/46 (0.93, 0.82–0.98); S3 emergencies 11/13 | v4 frozen before S3; same author, not independent |
| Router false alarms on v4 (25 non-urgent) | S2 2/25; S3 0/25 | Agent labels |
| S3 over-routing on unseen human text (ED dev, 2,873 prompts) | 1 urgent false alarm, 0 emergencies | Held-out for over-routing only; fixed afterwards |
| Reply guard on 218 real model replies | G1: 1 correct, 1 false positive, 1 miss; G2 (after audit fix): 2 correct, 0 false positives, 0 misses found | Agent review; small n |
| Browser, Intel UHD, Llama-3.2-1B q4f16, cached | startup 4.6 s; TTFT A 1.0 s, B 2.4 s; decode 5.6 tok/s; 0/6 failures | One machine, 3 repeats; RTX 4060 not used |
| Supportive quality | none | Blocked on ratings |

The figures behind these rows are indexed in `paper/figures/README.md`. The tables in `paper/tables/` are generated from the frozen JSON files rather than typed by hand.

## 10. Ethics and limitations

### 10.1 Ethics

The application is not a clinical service and says so. Urgent messages receive a fixed response with verified support information rather than a generated reply. No participant data is collected. All evaluation inputs are synthetic or come from a licensed public dataset used under its non-commercial terms. Adapters trained on EmpatheticDialogues inherit that licence and will not be published without a licence review. Any future human rating study needs ethical review before reviewers see sensitive scenarios.

### 10.2 Limitations

- **No quality evidence.** Every claim about supportiveness is withheld until independent blinded ratings exist.
- **Agent-authored safety labels.** v3 and v4 were written by the same agent that wrote S2 and S3, and that agent had seen the earlier misses. The first-run S3 recall of 0.93 is therefore optimistic. Post-hoc fixes raised it to 46/46, which is development evidence only. A set written by someone else is still needed.
- **Synthetic, mostly English inputs.** The scenarios are short. S3 covers a few French and Spanish phrases and nine multi-turn patterns. Wider multilingual and multi-turn coverage is untested.
- **One model, one machine.** The A/B measurements come from Python float32 on a single Windows laptop's CPU, and the host changed decode regime partway through a run for an unrecorded reason. The one browser run used a different model (Llama-3.2-1B) on the integrated Intel GPU, because Windows did not give the browser the RTX 4060.
- **Lexical flags.** The generative safety flags are pattern matches. They will miss paraphrased harm and can fire on harmless text.

### 10.3 Assistance disclosure

The code, analysis and much of the prose in both repositories were produced with a coding agent working under the author's direction, and the author reviews them. Results are reported from executed runs whose manifests are in the repository. Where a statement is a plan rather than a result, it is marked as such.

## References

See `paper/references.bib`. Every entry's verification status is in its `note` field. The Nature record of the Ibrahim et al. work was confirmed on 21 November 2026 through Oxford's repository; its full text has not been read.
