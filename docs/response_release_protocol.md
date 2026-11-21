# Protocol: when may generated text be shown?

**Working title:** From model output to user-visible response: safety, quality and latency in browser-based supportive dialogue

*Status: proposal, 21 November 2026. Agent-drafted from an external review and the project's own records, for Bushra's review and decision. No experiment in this document has been run. Nothing here is a result.*

## 1. The problem, as it actually happened

Relevia generates replies with a 1B model in the browser and streams them to the screen. A check on the finished reply can fix the saved transcript, but the user may already have read the problem. This has happened at each step of the reply guard:

- **G1** checked the whole text after every chunk, so "I cannot eng…" or half a phone number could appear before the pattern completed.
- **G2** showed finished, checked sentences plus the unfinished one when it looked harmless. An external review showed that "Child" passed and then became "Childline", which G2 removes.
- **G3**, the current version, shows only finished, checked sentences. That closed the leak, but the simulated median time to first visible text rose from 0.23 s to 2.55 s, and no reply is ever shown without a wait (`results/safety/reply-guard-v1/audit_g3.json`).

So the system has moved along a trade-off between exposure and delay without measuring either properly. Exposure has only been judged by the guard's own rules, which is circular. The delay was simulated at one decode rate, not timed in a browser. Nearby work ([release_policy_related_work.md](release_policy_related_work.md)) addresses streaming safety with white-box hidden-state probes on server GPUs (PlugGuard) or classifies user input only (MindGuard). It does not measure visible exposure for a text-only guard in a browser.

## 2. Questions

**Primary.** On identical recorded streams, how do release policies differ in the unsafe text they put on screen, the appropriate replies they wrongly withhold or replace, and the time until text first appears?

**Secondary (limited extension).** Do the quality and safety differences between prompt-only (B) and LoRA (C) replies persist once replies pass through the browser deployment and the chosen release policy? This depends on the approved LoRA pilot and is not needed for the primary study.

## 3. Policies compared

The review's draft labelled these G0–G3, which clashes with the guard's version names. Here they are **R0–R3**:

| Policy | Rule | Role |
|---|---|---|
| R0 | Stream immediately; check only the final reply | Measures exposure from checking too late. Run only offline on recorded streams |
| R1 | Hold the whole reply, check, then show it | Conservative latency bound |
| R2 | Release finished sentences that pass the check | The current app behaviour (guard version G3); strong simple baseline |
| R3 | Candidate prefix-safe release (below) | The proposed method |

**Candidate R3.** Release text up to the last point that no rule could still act on. A tail is held back while it could still grow into a blocked pattern ("Child" is a prefix of "Childline"; "I c" of "I cannot"; any digit of a phone number), or while a refusal has started but its kind depends on the rest of the sentence. Anything else is released word by word, as G2 did. The conversation context comes in through the existing rules, for example the user's own request deciding whether a refusal is legitimate. The aim is G2's speed without its leak.

R3 only protects against what the rules know about, and so does R2. Harm that a keyword list does not describe, or meaning that spans several sentences, passes both. That is why exposure is measured against independent labels, not against the guard. If R3 is no better than R2, the extra rule is not worth having, and that would be reported as the finding.

## 4. Data and design

**Streams.** Generate replies in the browser with WebLLM and record every chunk with its timestamp. The 217 existing research generations came from PyTorch and have no chunk timing, so they cannot be replayed faithfully. Replaying the same recorded streams through every policy isolates the policy from model variation. A smaller live run then measures real guard overhead, rendering and cancellation.

**Prompts.** The existing corpus had only 2 guard-relevant replies in 218, which is too few. The development set will be built to produce the failures of interest, using contrastive pairs that change one detail. Examples: grief without current danger against current risk; a past event against an ongoing one; a fictional character against a personal disclosure; a capability limit against a refusal to support; a contact detail split across chunks; ordinary numbers such as litres of water or breathing counts. Groups are split by underlying scenario, not wording. The final test set must be written by someone other than the method developer and frozen before R3 is fixed. CRADLE Bench and MindGuard's released test set are candidates for external input-side checks, after their terms are checked.

**Labels.** Two annotators independently mark unsafe spans in each reply (harmful specifics, invented or wrong contacts, inappropriate refusals) and whether the reply is appropriate. They follow written instructions, disagreements are recorded, and neither annotator sees the guard's decision. High-risk labels need a qualified reviewer. Agent-written cases are not described as clinically validated.

**Size.** The binding constraint is the number of replies that contain a labelled unsafe span. If a policy shows none of them on n such replies, the 95% upper bound on its visible-unsafe rate is about 3/n. So 100 positives bound it at 3%, and 300 at 1%. The final number depends on reviewer capacity and is fixed before the test set is opened.

## 5. Measures

Reported separately and never combined into one score:

- **Visible unsafe rate:** the share of positive replies where any labelled unsafe character reaches the screen.
- **Unsafe exposure:** labelled unsafe characters displayed, and for how long before removal.
- **False intervention rate:** appropriate replies withheld, cut or replaced.
- **Time to first visible text,** including the guard's hold, and **completion latency** to the final displayed reply.
- **Guard overhead:** time spent checking, separate from generation.
- **Supportive quality** of what is actually shown, rated independently on the EPITOME dimensions.

Results are shown as exposure against first-visible-text latency per policy, with confidence intervals and per-category tables.

## 6. What would count against the idea

These are fixed before testing:

- If R3's median time to first visible text is not at least 1 s shorter than R2's, R3 is not worth its complexity. The 1 s margin is a proposal for Bushra to confirm.
- If R3's visible unsafe rate is higher than R2's beyond the confidence interval, R3 is rejected, however fast it is.
- If R2 and R3 both show many labelled unsafe spans that the rules do not describe, the main finding is that text-only lexical release is insufficient, whatever its latency.

## 7. Limits and ethics

This is one model family, one browser and English only. Rule-based checks do not understand meaning. Simulated replay cannot reproduce rendering or cancellation, which the live run covers only partly. No participants are recruited for the primary study. Annotators are voluntary adults. Institutional ethics guidance is needed before recruiting anyone or collecting real disclosures. The test set would include high-risk synthetic content, so it is kept out of the public repository until its release is reviewed.

## 8. Order of work

1. Finish the full-method reading listed at the end of the related-work note, and narrow the claim.
2. Add chunk-timestamp recording to the app's research build, and implement R0, R1 and R3 next to the current R2, with every-prefix tests like those for G3.
3. Write the annotation guide, pilot it on the development set, and freeze the analysis plan.
4. Replay, then the live browser run, then independent labels and the analysis.

The LoRA extension waits for the approved pilot. Any comparison between PyTorch and browser output that also changes weights, quantisation or prompts is reported as a deployment-configuration comparison, with those confounds named.
