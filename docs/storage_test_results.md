# Storage and foundation test results

Date: 5 November 2026. JavaScript runner: Node v22.17.1 built-in `node:test`; no downloaded test framework or new runtime dependency. Python: 3.13.6 standard-library unittest. Dataset preprocessing additionally uses PyYAML 6.0.3, pinned in requirements-foundation.txt.

The storage suite injects a Map-backed storage adapter and a clock. This permits exact expiry and failure checks without a real user's data. It tests the production storage implementation, rather than an alternative implementation. Inference integration tests import the real brain after substituting Vite's build-time DEV constant and resolving module paths; they force GPU initialisation failure and prohibit fetch. No model is loaded. The legacy IndexedDB deletion test uses callback fakes and therefore does not establish browser transaction compatibility.

## Recorded outcomes

The JavaScript suite contains 18 tests covering default memory, explicit saving, explicit restore, isolation, read/write expiry, names, deletion, consent withdrawal, stale writes, page-end invalidation, quota failure, blocked storage, crisis retention, legacy keys, malformed records, no network storage operations, deterministic rules and failed GPU initialisation. All 18 passed in the recorded run. The Python foundation suite contains eight tests, all passing: deterministic grouped splits, leakage rejection, required model revision, unrated export, failure recording, duplicate/live-source rejection, preparation without generated responses, overwrite refusal, and rejection of unsupported adaptation conditions (some checks share one test).

Changed JavaScript files passed ESLint with `--max-warnings 0`. Full legacy lint remains failing: 41 errors and nine warnings, compared with 44 errors and 11 warnings before changes. The production build passed with the existing large-chunk warnings. These results refer to the installed dependency environment, not a newly provisioned machine. CI workflows were added but have not run on GitHub.

## Reproduction

From the application repository:

```powershell
npm test
npx --no-install eslint src/services/db.js src/services/chatStorage.js src/services/releviaBrain.js src/services/personalLetter.js src/services/groqApi.js src/components/Chatbot.jsx src/components/ChatPrivacy.jsx src/components/ErrorBoundary.jsx src/components/errorBoundaryHelpers.jsx tests/*.js eslint.config.js --max-warnings 0
npm run build
npm run lint
```

From the research repository:

```powershell
python -m unittest discover -s tests -v
python data/build_dataset.py
python scripts/check_leakage.py
python scripts/security_audit.py
```

The dataset builder uses existing local raw files in this run. No licensed dialogue content is copied into the test-result logs. Tests use synthetic strings; harness stub responses exist only in test memory or automatically cleaned temporary directories and are not scientific results.

## Failures encountered and interpretation

An initial lint invocation from the outer workspace failed because ESLint could not locate the app configuration; it was rerun from the correct repository. Changed Chatbot code exposed two pre-existing lint errors (the lowercase motion import and unused hasError parameter); these were corrected without disabling the rules. ErrorBoundary's mixed exports caused two warnings and were separated into a helper module.

A Python CLI test initially failed because the host's sandbox temporary directory denied file access. The test now uses a verified temporary subdirectory under the research tests directory, cleans it on exit and passes. An intermediate dataset report showed inconsistent counts while files were being replaced. JSONL writes now use temporary files followed by atomic replacement; the leakage checker hashes the same bytes it parses. Subsequent stable reads and deterministic rebuilds agree, including unchanged final-test checksums. Cross-file consistency during a concurrent rebuild is still not a database transaction: do not run generation while rebuilding data.

## Browser validation still open

The computer-use browser could not reach localhost:5173 or the correctly started 127.0.0.1:5174 server, returning connection timeouts. No visual pass is claimed. Before release, use a disposable browser profile and synthetic messages to verify: memory after reload and back navigation; opt-in/reopen; two tabs; deletion during generation; blocked storage; legacy database deletion; keyboard operation and mobile layout. Inspect browser storage and network requests, including voice separately. Do not use real distress disclosures for this check.

Passing the automated tests supports the implemented state-machine behaviour. It does not measure model safety, response quality, live WebGPU success, physical secure erasure or clinical benefit.


## Subsequent acceptance decision

On 5 November 2026, Bushra explicitly accepted the missing browser verification as an exception for local research work only. This records a scope-limited acceptance, not a successful browser test. Browser interaction, lifecycle, legacy IndexedDB and multi-tab checks remain required before release. The acceptance does not clear the archived dataset’s provenance or authorise its redistribution, model training, deployment or a public push. The recorded test outcomes are unchanged.
