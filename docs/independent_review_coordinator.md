# Preparing independent review

Bushra confirmed that reviewers are not available yet and requested prepared materials. The current status is **prepared, not reviewed**. No recruitment or external contact has taken place. Independent human evidence remains outstanding, so the relevant Milestone 3 acceptance criterion is incomplete.

The packet is stored in `results/experiment_01/independent_review_v1`. Give each future reviewer only their own `reviewer_1` or `reviewer_2` folder, containing `INSTRUCTIONS.md` and `ratings.csv`. Do not share the parent folder, generation script, manifest, condition key, model configuration or previous agent ratings. The key is ignored by Git, but ignoring a file does not prevent accidental manual sharing.

The prepared subset contains relocation, unwinding after a presentation and enjoyment of a painting. It excludes bereavement, caregiving, aggression, medical requests and immediate distress. This is a conservative selection for a preliminary ordinary-context exercise, not a guarantee that every reader will find the material comfortable. There are three independent scenarios and six responses per reviewer. The repeated A/B responses are not six independent scenarios.

Before distributing materials, review the instructions and confirm that the two voluntary adult reviewers are independent of prompt development and previous scoring. Record only an assigned reviewer identifier, relevant background, any prior exposure to the experiment, the rubric version and completion date in a private local record. No names, email addresses or personal health disclosures belong in the public research repository. If an institutional study is planned, resolve its applicable ethics requirements before recruitment; this packet does not supply institutional approval.

Keep returned files unchanged. Validate item identifiers, permitted score ranges, missing values and rationales before joining them to the private key. Preserve disagreements; any later adjudication should be recorded separately. Report each reviewer's ratings and missingness before calculating agreement. With just three scenarios, agreement estimates and paired confidence intervals will be unstable. Do not claim a reliable quality advantage from this subset. Do not treat these historical pilot items as a new independent test set.

The six quality dimensions include grounding, which was absent from the original five-dimension pilot. Original ratings and results remain unchanged. An expanded evaluation needs its own frozen dataset, responses and review export. These prepared sheets must not be relabelled as that larger evaluation.

Generation command, from the research repository:

```powershell
python scripts/prepare_independent_review.py
```

The exporter refuses to overwrite an existing packet. Its source hash records the exact original response file. Reproducible ordering does not make blinding cryptographically secure: the coordinator knows the conditions, and differences in response style or length can give reviewers clues. Report these limits when presenting the findings.
