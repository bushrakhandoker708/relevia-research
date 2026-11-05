# Literature notes and the gap

These are historical working notes, retained so that the development of the research question remains visible. Their original claim that every paper had been read in full is not established by the current evidence. Treat the detailed numerical and comparative statements below as claims requiring source verification, not as confirmed findings for a report.

Use [the audited literature-review notes](../research/notes/LITERATURE_REVIEW.md) for the recorded verification status. In particular, the account of *The Pursuit of Empathy* needs reconciliation with the paper’s reported conclusions. Full-text verification of the cited Nature study was not completed during this work. Neither note supports an established novelty claim. The proposed comparisons are research intentions, not completed experiments.

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
