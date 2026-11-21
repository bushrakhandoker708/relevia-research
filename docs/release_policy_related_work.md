# Related work for the response-release study

*Drafted with agent assistance on 21 November 2026, for Bushra's review. This is a targeted comparison of five papers, not a systematic review.*

## Why this comparison exists

The proposed study ([response_release_protocol.md](response_release_protocol.md)) asks when generated text may be shown to the user. Before building anything, I need to know how close existing work already is. An external review named PlugGuard, MindGuard and EmoSApp as the nearest papers, plus CRADLE Bench, Kharinaev et al., WebLLM and EPITOME as supporting references.

## What was read, and how closely

| Paper | Source read | Depth |
|---|---|---|
| Li et al., *PlugGuard*, ICML 2026 (PMLR 306:71360–71382) | PMLR PDF | Full text, searched for method, metrics, latency, over-blocking and limitations |
| Farinhas et al., *MindGuard*, arXiv:2602.00950v2 (NeurIPS 2026 Datasets and Benchmarks track, per arXiv comments) | arXiv HTML v2 | Sections 1–6 in full; appendices only through a summary, so appendix figures are not used here |
| Vimaleswar A et al., *EmoSApp*, IJCNLP-AACL 2025 | ACL Anthology PDF | Full text, searched for method, deployment, safety and limitations |
| Byun et al., *CRADLE Bench*, EACL 2026 | ACL Anthology PDF | Data, annotation and ethics sections |
| Ruan et al., *WebLLM*, arXiv:2412.15803v2 | arXiv HTML v2 | Full text |
| Sharma et al., *EPITOME*, EMNLP 2020 | ACL Anthology PDF | Framework section |
| Kharinaev et al., quantisation and safety | Not retrieved this time | Only the earlier abstract note in [literature.md](literature.md). The IEEE page refused automated access, so the IEEE Access 2026 version mentioned by the review is **not verified** |

## Method comparison

| | PlugGuard | MindGuard | EmoSApp | Relevia G3 (current) |
|---|---|---|---|---|
| What is checked | The model's output, token by token | The user's messages only ("input classification") | Nothing separate; safety comes from the fine-tuned model and system prompt | User input (S3 routing) and model output (reply guard) |
| Signal | Hidden states of an intermediate layer of the frozen generating model, plus a 20M-parameter recurrent head | Text of the current user turn and the whole earlier conversation | Not applicable | Text only; keyword rules |
| Access needed | White-box: the guard reads the protected model's activations | Black-box text | Not applicable | Black-box text |
| When it decides | Every token; a single token over the threshold stops the response | Once per completed user turn | Not applicable | At each finished sentence; the unfinished one is held back |
| What happens on detection | Generation stops ("stop-if-harmful"). Tokens before the trigger have already been emitted | Flags the turn; in their system test a developer message steers the clinician model | Not applicable | Replace the reply, or remove the sentence with an unverified contact |
| Domain | General safety: prompts from WildGuard, S-Eval, MMSafetyBench and FigStep | Mental-health support: safe, self-harm, harm to others | Mild emotional and mental-health concerns | Supportive dialogue |
| Main metric | Response-level and streaming F1 | AUROC, false-positive rate at fixed recall, and whether the first unsafe turn is flagged on time | Benchmarks, plus student and professional ratings (including a 1–5 safety rating) | Agent-labelled activations on 218 replies; simulated lag |
| Measures text shown before a stop | Not found. Streaming F1 counts a response as caught if any token triggers, wherever that is. Their Figure 5 gives where the first harmful token falls (48% at positions 10–49) but not how much was displayed | Not applicable (no output check) | No | Not yet: the guard's own lexicon cannot be its own ground truth |
| Latency measured | Guard compute overhead: +0.43 s over 1,024 tokens sequentially, under 1 ms in parallel mode, on Qwen3-8B with server GPUs | None; large reasoning judges are described as too slow, without figures | On one phone: 13.5 tok/s and 5.69 s time to first token for the deployed model | Simulated time to first visible text (median 2.55 s at 5.6 tok/s) |
| Deployment target | Server GPUs (NVIDIA L20 and H20) | Not stated | Android, through ExecuTorch | Browser, through WebLLM on WebGPU |
| Labels | Kimi-K2 as labeller, chosen against 10 safety experts' majority vote on 1,000 samples | Three licensed clinical psychologists on the test set (Krippendorff's alpha 0.57); synthetic training data labelled by GLM-4.6 | Human ratings of conversations | Agent labels |

## What each paper means for the study

**PlugGuard** is the closest. It names the same problem: a post-hoc check "may expose unsafe content before it is caught". It solves it inside the model, by reading hidden states at every token. Three things differ from Relevia's setting. First, it needs activations from the generating model. WebLLM's public chat API returns text, and I have not checked whether its internals could expose intermediate hidden states. Second, its intervention is to stop, which leaves the tokens before the trigger on screen. Third, its benchmark is general safety, so it does not cover over-refusal of grief or invented helpline numbers. These differences make a text-only release policy worth testing. They do not show that one would be better. PlugGuard could well catch harms that keyword rules never will.

**MindGuard** shows that clinically grounded, multi-turn risk classification of *user* messages already exists, with released data and 4B/8B models. A context-aware input classifier would therefore overlap heavily with it. It is relevant here in two ways. Its three-class label scheme and clinician annotation are a model for the input side. And its classifiers are 4–8B parameters, larger than the 1B model Relevia runs in the browser, so they could not simply be added to the browser as they are. It does not check model output or streaming.

**EmoSApp** is the closest *application*: the same Llama-3.2-1B-Instruct base, fine-tuned with quantisation-aware LoRA and run offline. Its limitations section reports that the model "only provides crisis helpline numbers for the USA". That is the same failure that started Relevia's reply guard, which supports treating invented or wrong contacts as a real failure mode, not a hypothetical one. EmoSApp has no separate output check, so local inference and a small adapted model are not novel by themselves.

**CRADLE Bench** labels Reddit posts with seven crisis types and an ongoing/past tag, annotated by four mental-health professionals. It labels user text, not model replies. It could serve as an external test of S3's current-versus-historical handling, after checking access terms. It does not measure what the reply guard does.

**WebLLM** reports decoding throughput only (for example Llama-3.1-8B at 41.1 tok/s in Chrome against 57.7 tok/s natively on an M3 Max). It does not evaluate safety or what the user sees while text streams. It is the systems base, not prior work on release policies.

**EPITOME** gives three empathy dimensions (emotional reactions, interpretations, explorations), each rated none, weak or strong, from TalkLife and Reddit data. It remains the structure for quality ratings, so that "supportive quality" is not an unexplained score.

## What this leaves open, stated carefully

In these papers I did not find a measure of **how much independently labelled unsafe text reaches the screen** under different release policies, alongside **time to first visible text**, for a **text-only guard in a browser**, in **supportive dialogue** where over-refusal is itself a harm. That is a gap in five papers, not a gap in the field. Before any novelty claim I still need to read the streaming-guardrail work PlugGuard compares with (Xuan et al. 2025; Krishna et al. 2025; Li et al. 2025, FineHarm), search for work on buffering or delayed display in chat interfaces, and read the MindGuard appendices and Kharinaev et al. in full.
