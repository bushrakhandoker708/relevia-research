# Privacy and threat model — proposed controls, not implemented guarantees

## Assets and boundaries

Assets include raw messages, inferred distress, names, journal entries/drafts, visit history, model outputs, local credentials and research datasets. Browser origin isolation separates websites; it does not separate people sharing a browser profile. A UID field is not authentication. IndexedDB is not differential privacy and does not provide application-managed encryption.

The inference path stays within the browser according to inspected source, but the application downloads model assets and includes analytics. Speech synthesis may depend on browser/OS services; source alone cannot prove that every voice is local. No network capture was performed. An absence of explicit chat upload in the active inference path is narrower than “nothing leaves the device.”

## Threats and controls

| Threat | Current exposure | Proposed control and residual risk |
|---|---|---|
| Shared-device disclosure | Shared chat/name; Home letter exposes previous context | Session-only default; opt-in local profiles, private letter opt-in; device owner/extensions can still read local data |
| Stale sensitive records | Cleanup requires a later write; names persist | Filter expired data before reads, prune on open/write; browser closure prevents guaranteed physical deletion at exact expiry |
| Console/diagnostic disclosure | Text/name logs; error records in localStorage | Remove sensitive logs and minimize error data; browser tools may retain earlier logs |
| XSS/dependency compromise | Same-origin script access to local data | Minimize dependencies, review CSP, avoid raw HTML rendering, dependency review; local processing does not eliminate supply-chain risk |
| Cloud credential theft | Legacy frontend VITE key path | Remove unused path; if needed later use authenticated, rate-limited backend; rotation requires provider action |
| Accidental research reuse | Local chat and archived data can be mistaken for training data | Explicit provenance allowlist; never ingest live conversations by default; separate research output directories |
| Deletion races | In-flight generation can write after clear | Session generation/version token invalidated by deletion; tests across tabs and failures |

## Proposed retention contract

Default: messages and optional name remain in memory for the current chat only. Persistent history requires a clear opt-in explaining data categories, shared-device visibility, expiry and deletion. Offer session-only and a bounded retention option; the initial candidate is 24 hours, not a scientifically justified optimum. Keep crisis text out of persistent storage by default; transient context can maintain continuity without retaining it across visits. Do not derive durable emotional profiles.

On open and every read, exclude expired records before returning them; physical cleanup runs while the application is active. Persisted names follow the chosen retention policy. Migration must not silently assign legacy shared history to a new user/profile. Offer informed deletion of legacy records. Chat deletion must clear displayed text, memory, names and associated persistent records; whole-app deletion additionally covers journals, drafts, visits, settings and error logs. Distinguish model cache removal from personal-data deletion.

These are proposed requirements. They are deliberately not retroactive claims about the present application. Implementation needs IndexedDB tests with an injected clock and browser tests for reload, blocked storage, migration, multiple tabs and deletion during generation.

## Research and release boundary

Use synthetic development fixtures and appropriately licensed research datasets. Keep raw data, real conversations, credentials and model weights out of new commits. Record source-specific terms; do not assume academic dataset access licenses a public adapted model. No participants are recruited in this milestone. Determine institutional ethics/data-protection requirements before any participant study; consent alone is not the release criterion.

NIST's [Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) informs risk documentation and evaluation, and [WHO's 2024 guidance announcement](https://www.who.int/news/item/18-01-2024-who-releases-ai-ethics-and-governance-guidance-for-large-multi-modal-models) motivates scrutiny of health-related use. Neither certifies Relevia. This document is an engineering threat model, not a legal-compliance determination.
