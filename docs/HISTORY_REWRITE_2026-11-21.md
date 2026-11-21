# Commit hashes before and after the history rewrites of 21 November 2026

On 21 November 2026 the histories of both repositories were rewritten. In the application repository this removed personal contact details and personal photographs from earlier commits and built files, and then two working-notes files. In this repository it removed the same two working-notes files, which are now kept privately, and replaced personal contact details in the original copy of `results/completion_2026_11_07/lint_before.log` (see `REDACTION.md` there). The application repository was also recreated on GitHub from its rewritten history. File contents are otherwise unchanged, but commit hashes changed.

Records in this repository keep the hashes they were written with, because rewriting them would change what was recorded at the time. Use these tables to find the same commit in the current histories.

## Application repository

| Hash cited here | Current hash | Cited in |
|---|---|---|
| `d6d2ec2` | `ef13648` | `docs/architecture_audit.md`, `docs/decision_log.md`, `docs/milestone_2_report.md`, `results/audit/snapshot.json` |
| `57cb4ca` | `ff28e7a` | `docs/milestone_3_report.md`, `results/milestone_3/source_state.json`, `results/milestone_3_completion/preservation_manifest.json` |
| `0b8df47` | `7f23765` | `docs/MILESTONE_3_CLOSURE.md` |
| `cfa1783` | `6eeaece` | `detectors/README.md`, `docs/MILESTONE_4_1_REPORT.md`, `docs/safety_failure_taxonomy.md`, `scripts/audit_reply_guard.mjs` |
| `46e9cf0` | `2cb5f36` | `detectors/README.md`, `docs/MILESTONE_4_1_REPORT.md`, `scripts/audit_reply_guard.mjs` |
| `3195335` | `f418001` | `detectors/README.md`, `docs/REPRODUCIBILITY_AUDIT_2026-11-21.md`, `scripts/replay_release.mjs`, `tests/test_replay_release.py` |

Two application commits no longer exist: one only renamed a photograph and one only added a build tool's archive. The old `gh-pages` branch, which held built copies of the site, was not carried over.

## This repository

| Hash cited here | Current hash | Cited in |
|---|---|---|
| `413ffd5` | `413ffd5` (unchanged) | `archive/README.md`, `docs/dataset_provenance_report.md` |
| `2b9699c` | `e6bb35e` | `archive/README.md` |
| `3c5656a` | `155ecba` | `docs/milestone_3_report.md`, `results/experiment_01/*/manifest.json`, `results/milestone_3/source_state.json` |
| `286bd42` | `0eb96c8` | `docs/MILESTONE_3_CLOSURE.md` |
| `f76179c` | `b11aaed` | `docs/MILESTONE_4_1_REPORT.md` |
| `8c5d48f` | `6ab5bac` | `docs/MILESTONE_4_1_REPORT.md` |
| `b1a85fd` | `fdc752f` | `docs/MILESTONE_4_1_REPORT.md` |
| `c164cac` | `d0ad9f5` | `docs/REPRODUCIBILITY_AUDIT_2026-11-21.md` |
| `772ba99` | `9673d9a` | the commit message that added `results/completion_2026_11_07/REDACTION.md` |

The frozen detector and policy copies in `detectors/` are verified by file hash, not by commit, so their checks are unaffected.
