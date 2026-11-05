# Development/validation leakage repair

The old builder selected four first-turn examples from official validation conversations, then removed only those example IDs. Five other rows from their conversations remained in validation, so evaluation could receive familiar context even when the selected row itself was absent. Conversation turns are dependent observations; row-level disjointness was insufficient.

The identified examples and remaining validation rows were:

| Former few-shot ID | Remaining validation IDs |
|---|---|
| hit:8618_conv:17236_t2 | hit:8618_conv:17236_t4 |
| hit:2701_conv:5402_t2 | hit:2701_conv:5402_t4; hit:2701_conv:5402_t6 |
| hit:3758_conv:7517_t2 | hit:3758_conv:7517_t4 |
| hit:7735_conv:15471_t2 | hit:7735_conv:15471_t6 |

The prior 4,539 validation rows now become 4,534 after excluding those five rows. The four previously used examples are also excluded from the new few-shot set. We do not restore those exposed examples to validation and pretend their prior use has disappeared. The four conversation groups are recorded as quarantined in split_info.json.

`src/splits.py` reserves ten percent of sorted official-training conversation IDs using seed 42. It chooses four eligible, emotion-diverse first-turn examples from that reserved pool, removes their entire groups from the remaining development set, and excludes all reserved development groups from training. Prompt decisions use dev; validation is reserved for model selection. Official test membership and the previously frozen test-file bytes remain unchanged. This separation is preferable to merely removing four rows or choosing new validation examples because it stops prompt construction from drawing on validation material.

| Partition | Rows after repair |
|---|---:|
| train | 25,721 |
| dev | 2,873 |
| fewshot | 4 |
| val | 4,534 |
| test_seen | 4,181 |
| test_unseen | 839 |

All 15 pairwise conversation-group intersections are zero. Test SHA-256 values remain `ffc6a077ab3ae3a60e5fc89c3134cc0470358bc3cae40bb4c01f6828cf5f3228` and `4f57411194896c3a6236335eebabceb5899a43966f435bc11bc52d212f7a2e09` respectively. Machine-readable before/after evidence is in results/milestone_2/leakage-before.json and leakage.json.

For exact test-order preservation, the builder replays the original seeded shuffle sequence in memory before replacing the training/development allocation. The old validation example selection in that compatibility step is used only to identify previously exposed groups and preserve shuffle history; those examples are not delivered to the new prompt. This is a deliberate compatibility choice, not a recommended pattern for a new dataset pipeline.

`scripts/check_leakage.py` fails on any conversation overlap and, when the baseline manifest is available, fails if frozen test bytes change. `common.write_jsonl` now replaces completed files atomically. Notebook commands and configuration notes point prompt evaluation at dev rather than val. The original training validation remains for model selection. Older unlogged manual prompt experiments cannot be retrospectively erased; the report therefore does not claim that every historical decision was independent of validation.

Limitations: conversation IDs do not detect near-duplicate content under different IDs, topic overlap, pretraining contamination, PII or licence violations. The archived empathy_42k dataset is not used. Its archive README describes 15,000 incorrectly paired ED rows and unreliable earlier dataset claims; a complete provenance/privacy review is still required before endorsing redistribution. No dataset content was newly committed or uploaded in this milestone.
