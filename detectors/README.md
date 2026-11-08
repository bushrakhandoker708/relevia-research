# Frozen detectors

`s1/` is a byte-identical copy of the application's `src/services/safety.js` (and its `consts.js` import) at the S1 freeze. Its SHA-256 matches `detector_sha256` in `data/safety_v2/freeze.json`. `scripts/evaluate_safety.mjs` evaluates this copy, so the S1 evidence stays reproducible after the application moves to S2. Do not edit these files. A new detector gets a new folder and a new freeze.
