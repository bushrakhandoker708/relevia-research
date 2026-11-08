# Edinburgh research brief: 8 November 2026

This brief replaces nothing. It updates `EDINBURGH_RESEARCH_READINESS.md` (7 November) with the Milestone 4 work. It is written for a prospective supervisor in the CDT in Machine Learning Systems (Round 1 deadline 14 December 2026). Coding agents assisted with the work and the drafting, and the author reviews it.

## The question in one paragraph

For a small language model that runs on the user's own device, is it better to invest in the prompt or in a parameter-efficient adapter? "Better" has to be judged jointly on supportive reply quality, on safety (routing and generated content) and on runtime cost on real consumer hardware. The project holds the model fixed (Qwen2.5-1.5B-Instruct at a pinned revision) and changes one factor at a time. A is a minimal prompt, B a developed prompt and C is B plus a LoRA adapter. The B–C comparison isolates the effect of the weights.

## What exists and can be inspected

| Area | Evidence | What it does not show |
|---|---|---|
| Data hygiene | Zero group overlap across 15 partition pairs; quarantined archive; hash-frozen inputs | Anything about quality |
| Prompting (A vs B, 60 pairs) | B: 1/60 token-cap hits against 30/60 for A; 19 tokens shorter; +2.4 s to the first token and +0.05 s per token on CPU | Whether B is more supportive (0/120 items rated) |
| Systems confounds | A headline latency effect traced to response length plus a Windows Modern Standby overlap and a host decode-regime shift | Browser behaviour |
| Safety routing | S0 → S1 → S2, each tested on a set frozen before it was written. S2 recall 18/24 (0.55–0.88) on v3 with 0/18 false alarms; McNemar against S1 p ≈ 0.004 | Independent validity, because the same agent wrote the v3 set and S2 |
| Generated-reply safety | A reply guard in the app after a logged refusal that also gave an outdated hotline number; a lexical generative probe on the v3 messages | Rated harm |
| Adaptation | A LoRA pipeline that changes only the adapter, cannot read the final test set and has passed a smoke test (4 CPU steps, validation loss 4.02 → 3.67) | That LoRA helps; the pilot has not run |
| Browser cost | Instrumentation for cold and cached startup, TTFT, runtime prefill and decode rates, failure rate, switching and unloading | Any measurement; on the development laptop the browser picks the integrated GPU |
| Write-up | `paper/manuscript.md` with a claim–evidence matrix and generated tables | A finished paper or a novelty claim |

## Why it is an ML-systems question

Three findings so far are systems findings rather than modelling ones. A prompt change altered latency mainly by changing output length. Host power states produced the largest single "effect" in the timing data. And the hardware that actually runs the model is chosen by the operating system and browser, not by the application. Any adapter result will have to survive the same scrutiny. A next study would treat model size, quantisation, runtime and device class as separate factors, and would charge model loading and switching to any routing scheme.

## Honest gaps

- No independent human ratings, so no quality claim of any kind.
- The safety labels are synthetic and agent-authored, with no clinical input.
- English only, single-turn and short inputs.
- One laptop, CPU only for model measurements.
- The literature review is incomplete, so originality is not claimed.

## What would make it strong by December

1. Two blinded reviewers rate a feasible subset of the 120 A/B replies, with agreement reported.
2. An approved LoRA pilot on a GPU, with the learning rate chosen on validation data, then B against C on the unchanged final set.
3. One browser benchmark run per adapter choice, with the hardware recorded.
4. A safety set written by someone other than the detector's author.

## Questions for a supervisor

- Is the prompt-versus-adapter trade-off under device constraints a useful CDT question, or should the systems axis (quantisation, runtime, device) lead?
- What annotation design and sample size would make a supportive-quality claim credible at this scale?
- How should host power states, caching and GPU selection enter a benchmark protocol?
- What safety coverage is needed before any participant study?
