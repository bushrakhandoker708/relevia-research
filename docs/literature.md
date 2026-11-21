# Literature notes and the gap

These are historical working notes, retained so that the development of the research question remains visible. Their original claim that every paper had been read in full is not established by the current evidence. Treat the detailed numerical and comparative statements below as claims requiring source verification, not as confirmed findings for a report.

Use [the audited literature-review notes](../research/notes/LITERATURE_REVIEW.md) for the recorded verification status. In particular, the account of *The Pursuit of Empathy* needs reconciliation with the paper’s reported conclusions. Full-text verification of the cited Nature study was not completed during this work. Neither note supports an established novelty claim. The proposed comparisons are research intentions, not completed experiments.

> **Correction, 8 November 2026.** The BN et al. summary below says fine-tuning was "not clearly better". The paper's arXiv abstract (2505.15065) says the opposite: fine-tuning improved similarity to reference replies and perceived empathy, with gains that varied and a ceiling for the smallest models. The "26 vs 22 comparisons" figure is not in the abstract and has not been checked against the full text. Treat that summary as withdrawn. The Ibrahim et al. work had then been verified only as arXiv:2507.21919 (2025), under a different title.

> **Update, 21 November 2026.** The Nature article named below is now confirmed: *Nature* 652(8112), 1159–1165, published 29 April 2026, doi:10.1038/s41586-026-10410-0. The record was checked on Oxford's repository (ORA); the publisher's full text was not read, so the figures in that entry remain unchecked. Two closely related papers were missing from these notes and are added under "Closest work": EmoSApp and Kharinaev et al.

## Closest work

**BN et al., EMNLP 2025: "The Pursuit of Empathy: Evaluating Small Language Models for PTSD Dialogue Support"**
- 8 small models (0.5B–5B, including Llama-3.2-1B/3B and Qwen2.5-0.5B/1.5B/3B), zero-shot vs. LoRA fine-tuned, on TIDE (10k synthetic PTSD two-turn dialogues, reference replies from Claude Sonnet 3.5, CC BY-NC 4.0).
- Human eval: N=116 Prolific raters, a single 5-point empathy scale. Zero-shot beat fine-tuned in 26 comparisons, fine-tuned beat zero-shot in 22, so fine-tuning was **not** clearly better. They suggest small models overfit to "affirmation-heavy" synthetic replies.
- Fine-tune settings: LoRA r=8, lr 1e-5, **max length 80**, 3 epochs, 6k train rows.
- Their own limitations: no adversarial testing for harmful advice or crisis mishandling; single Likert scale; two-turn only.
- **What they didn't do, and I will:** a tuned/few-shot prompting baseline; EPITOME-dimension ratings; crisis and sycophancy safety tests; any deployment measurement.

**Ibrahim, Hafner & Rocher, Nature 652 (2026): "Training language models to be warm can reduce accuracy and increase sycophancy"**
- Warmth SFT on Llama-3.1-8B, Mistral-Small, Qwen-2.5-32B, Llama-3.1-70B and GPT-4o: +10 to +30 pp error rate, about 40% more agreement with incorrect user beliefs, **worst when the user expresses sadness**.
- A system-prompt version (tested only on 32B, 70B and GPT-4o) showed similar but weaker and less consistent effects.
- **Gap:** the smallest model is 8B, and the prompt-vs-fine-tune comparison wasn't done on small models. My RQ2 tests both at 1–3B.

**A et al., IJCNLP-AACL 2025: "An Offline Mobile Conversational Agent for Mental Health Support" (EmoSApp; arXiv:2507.10580; doi:10.18653/v1/2025.ijcnlp-long.191)**

*Added 21 Nov 2026. Abstract only; full text not read.*
- Fine-tuned and quantised Llama-3.2-1B-Instruct, the same model Relevia ships by default. It runs fully offline on Android phones.
- Trained on mental-health question–answer pairs and multi-turn dialogue. Full fine-tuning, LoRA with post-training quantisation, and quantisation-aware LoRA are compared, according to search summaries; check this in the full text.
- Evaluated qualitatively with students and mental-health professionals, and on nine commonsense and reasoning benchmarks plus two mental-health datasets.
- **Consequence for Relevia:** "a small quantised on-device model for emotional support" is already published. So is LoRA combined with quantisation on this model. The abstract does not mention crisis escalation, safety routing, browser or WebGPU deployment, or measuring the gap between the evaluated and the deployed configuration.

**Kharinaev et al., 2025: "Investigating the Impact of Quantization Methods on the Safety and Reliability of Large Language Models" (arXiv:2502.15799)**

*Added 21 Nov 2026. Abstract only.*
- Covers 66 quantised variants of four models, using four post-training and two quantisation-aware methods.
- Human safety evaluation, plus a new 1,067-question OpenMiniSafety set and four existing benchmarks.
- Main finding: both post-training and quantisation-aware quantisation can degrade safety alignment, and no method is consistently best.
- **Consequence for Relevia:** quantisation-induced safety loss is established in general. What remains open is whether it affects supportive-dialogue outcomes (escalation, over-refusal, harmful agreement), and whether changing the *runtime* (PyTorch to MLC on WebGPU) matters separately from quantisation. My searches on 21 Nov found no paper on the runtime question. That is a reading gap, not a novelty claim.

## Methods references

- **Sharma et al., EMNLP 2020 (EPITOME):** empathy = Emotional Reactions, Interpretations, Explorations, each none/weak/strong. → my human rating rubric (`docs/rating_guide.md`).
- **Rashkin et al., ACL 2019 (EmpatheticDialogues):** 24,850 conversations, 32 emotion labels, official splits 19,533/2,770/2,547 split by speaker. → my data source + held-out-emotion test.
- **Dettmers et al., NeurIPS 2023 (QLoRA):** 4-bit frozen base + trainable LoRA adapters. → my training method.

## Background only

- **Kermani et al., CLPsych 2025:** fine-tuning vs. prompting vs. RAG on Llama 3, but for **classification** (emotion and condition detection), not reply generation. Fine-tuning got the best accuracy. Cite it as related, not as an answer to my question. CLPsych is also a good target venue.

## Still to read before I claim novelty

All are cited in BN et al.:
- Qian et al. 2023: LLMs for empathetic response generation (EmpatheticDialogues)
- Loh & Raamkumar 2023: LLM empathetic responses for online counselling
- Filienko et al. 2024: comparing prompting techniques for problem-solving therapy
- Park et al. 2024: safety metrics for mental health chatbots
- Lee et al. 2023: Chain of Empathy prompting

## Working research question

> For small (1–3B) quantized language models, does empathy fine-tuning beat a carefully tuned prompt on unseen emotional situations, and does it cost more in sycophancy and crisis-handling safety, when deployed in a real browser on ordinary laptops?

- **RQ1 (quality):** zero-shot vs. tuned prompt vs. fine-tuned, EPITOME ratings, on held-out ED emotions (+ TIDE for comparability with BN et al.)
- **RQ2 (safety):** crisis handling + Nature-style sycophancy (neutral vs. sad framing)
- **RQ3 (deployment):** load time, time to first token, tokens/s and memory in the Relevia browser app (WebLLM)
