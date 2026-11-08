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

## Expanded evaluation continuation — 7 November 2026

The new 60-scenario run has a separate frozen protocol in `expanded_baseline_protocol.md`. After generation completes, `summarise_controlled.py` prepares separate reviewer folders with blank six-dimension scores and independent order randomisation. These are new packets, not additions to the three-scenario historical pilot. Send only each reviewer's folder. The complete repository exposes prompts, identities and previous ratings, so it is unsuitable as a blinded packet.

`analyse_independent_ratings.py` accepts two returned CSVs, the private mapping key and the scenario JSONL. It validates score ranges and item identities, rejects entirely blank annotations, reports paired summaries separately for each reviewer and category, and computes quadratic-weighted kappa only for jointly rated items. Missing scores are not zero. Constant marginals can make kappa undefined; the output remains null in that case. Independence and adult participation require coordinator confirmation; the script cannot establish either from a filename.

No returned sheets exist at this stage. Do not run the analysis on fabricated scores or describe exporter-generated blank fields as human evidence.
