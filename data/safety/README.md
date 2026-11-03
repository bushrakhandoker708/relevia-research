# Safety test sets (RQ2)

These are **seed sets** that show the format. Before the real study, I expand them and get my supervisor to review them.

| File | Now | Target | What it tests |
|---|---|---|---|
| `crisis.jsonl` | 8 crisis + 4 control | ~150 crisis + ~75 control | Does the model take risk seriously and point to real help? Controls ("work is killing me") check it doesn't panic at figures of speech. |
| `sycophancy.jsonl` | 5 beliefs × 2 variants | ~75 beliefs × 2 variants | Does the model agree with a false or harmful belief, and is that worse when the user sounds sad? (Same design as Ibrahim et al., *Nature* 2026, scaled down to 1–3B models.) |

## Fields

- `crisis.jsonl`: `id`, `kind` (direct / indirect / self_harm / control), `is_crisis`, `prompt`, `history`
- `sycophancy.jsonl`: `id`, `belief_id`, `variant` (neutral / sad), `prompt`, `false_belief`, `correct_position`, `history`

## Rules I follow when adding items

- Every belief needs a `correct_position` I can back with a reliable source (NHS, NIMH, WHO). Write the source in `docs/safety_sources.md`.
- Crisis items stay non-graphic. Indirect phrasings matter most, because keyword filters miss them.
- Never add items copied from real people's posts.
- These sets are for **evaluation only**. Nothing in here ever goes into training data.
