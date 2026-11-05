# Safety test sets (RQ2)

These are preliminary seed sets for a proposed evaluation, not a validated safety benchmark. I still need to expand and review the scenarios before drawing conclusions. Supervisor review is a planned step; it is not recorded as completed. The targets below belong to the earlier expanded study and differ from the smaller Experiment 01 pilot.

| File | Now | Target | What it tests |
|---|---|---|---|
| `crisis.jsonl` | 8 crisis + 4 control | ~150 crisis + ~75 control | Does the model take risk seriously and point to real help? Controls ("work is killing me") check it doesn't panic at figures of speech. |
| `sycophancy.jsonl` | 5 beliefs × 2 variants | ~75 beliefs × 2 variants | Does the model agree with a false or harmful belief, and is that worse when the user sounds sad? The earlier notes propose a comparison with Ibrahim et al.; equivalence to that study’s design has not been verified. |

## Fields

- `crisis.jsonl`: `id`, `kind` (direct / indirect / self_harm / control), `is_crisis`, `prompt`, `history`
- `sycophancy.jsonl`: `id`, `belief_id`, `variant` (neutral / sad), `prompt`, `false_belief`, `correct_position`, `history`

## Rules for adding items

- Every belief needs a `correct_position` I can back with a reliable source (NHS, NIMH, WHO). Write the source in `docs/safety_sources.md`.
- Crisis items stay non-graphic. Indirect phrasings matter most, because keyword filters miss them.
- Never add items copied from real people's posts.
- These sets are for **evaluation only**. Nothing in here ever goes into training data.
