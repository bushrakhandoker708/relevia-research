# Frozen detectors

`s1/` is a byte-identical copy of the application's `src/services/safety.js` (and its `consts.js` import) at the S1 freeze. Its SHA-256 matches `detector_sha256` in `data/safety_v2/freeze.json`. `scripts/evaluate_safety.mjs` evaluates this copy, so the S1 evidence stays reproducible after the application moves to S2. Do not edit these files. A new detector gets a new folder and a new freeze.

`s2/` is a byte-identical copy of the application's S2 `safety.js` (SHA-256 `55341a76…`, matching `s2_sha256` in `results/safety/s2-v1/evaluation.json`) and the `consts.js` it shipped with.

`s3/` is the S3 version evaluated in `results/safety/s3-v1-final/` (application file SHA-256 `3e4bbd8b…`). The only change from the application file is its import path, `./safety.js` → `../s2/safety.js`, so it runs from here. The S3 code used for the **first** v4 run (`results/safety/s3-v1/`, SHA-256 `c6fda965…`) was not saved as a file. Its hash and per-case outputs are the record.

`guard_g1/` is reply guard version 1 as committed in the application at `cfa1783`, used by `scripts/audit_reply_guard.mjs`.

`guard_g2/` is reply guard version 2 as committed in the application at `46e9cf0` (`replyGuard.js` SHA-256 prefix `a2fc45bb1bb7f06b`), with the `consts.js` it imported. The audit compares it with the application's current G3.
