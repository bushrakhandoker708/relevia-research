# Milestone 2 privacy design decisions

Date: 5 November 2026. This document describes implemented controls, their tests and their boundaries. It is not a clinical, legal or security certification.

## D005 — Memory is the default storage boundary

The previous application opened one IndexedDB database for every user, ignored the supplied UID, and read the same history for both chat generation and the Home letter. Renaming the UID would not have corrected this because the database queries did not partition records. More importantly, automatically retaining sensitive conversation content was unnecessary for the immediate interaction.

The implementation now creates an unpredictable session identifier for each page instance and stores chat state in a Map keyed by that identifier. `src/services/chatStorage.js` owns this policy; `db.js` is a small compatibility facade, and `Chatbot.jsx` supplies the session identifier explicitly. Memory survives ordinary interaction within the current page, but no session identifier or default chat is placed in localStorage or sessionStorage. The pagehide handler invalidates in-memory sessions and pending responses. Names are memory-only metadata with the same 24-hour logical expiry; a name inside an explicitly saved message remains message content.

Alternatives included retaining IndexedDB with per-user indexes, implementing authentication, or encrypting data using a key stored beside it. IndexedDB partitioning would still leave automatic persistence as the default; authentication would expand scope; colocated encryption would not protect against same-origin scripts or a shared browser user. Memory-first storage therefore provides a smaller, testable boundary without pretending to solve identity management.

Tests establish that no storage writes occur during default chat, a fresh store cannot recover the prior memory, independent IDs receive separate history, and page-end invalidation prevents stale handles from writing. They do not establish browser crash-dump secrecy, secure erasure of RAM or protection from malicious extensions. Browser lifecycle and rendered UI checks remain open because the available browser connection could not reach the local server.

## D006 — Explicit, bounded saving and deliberate reopening

The `ChatPrivacy.jsx` disclosure explains purpose, duration, deletion and shared-device visibility before its unchecked saving control. Saving writes at most 100 message records under a session-specific `relevia_chat_v2:` key. Reopening requires an explicit saved-chat selection; the application never imports another session automatically. Reopening copies eligible records into a fresh in-memory session, removes the prior saved copy and leaves saving disabled. The list shows timestamps rather than message excerpts.

The alternative of automatically restoring the latest saved chat would recreate the shared-device disclosure problem. A random identifier alone cannot authenticate a human. Therefore the UI explicitly states that other people using the browser can deliberately open saved chats. The supported claim is separation of automatic contexts, not access control between people sharing an unlocked browser profile. Simultaneous manual restores in separate tabs are not an authenticated ownership protocol and require additional browser testing.

Logical expiry is applied to memory reads, writes and saved-record decoding. Saved-list inspection removes expired or malformed records. Saving failure disables further saving, keeps the generated reply in memory and displays that an older saved copy may remain. Browser closure cannot run cleanup code, so physical erasure exactly 24 hours after a timestamp is not promised. localStorage was chosen for small bounded snapshots and synchronous failure handling; it is not appropriate for large histories and can block the main thread. A future measured migration to IndexedDB can retain the same policy interface.

## D007 — Deletion is a state transition, not only a disk operation

Deleting a saved record alone is insufficient: a pending generation could restore it moments later. Each storage handle captures a session epoch, and clearing or changing consent increments that epoch. Stale handles cannot append messages or names. The UI has an independent generation epoch so late tokens, final replies and scheduled speech do not repopulate the cleared conversation. Deletion clears chat state, saved chat keys, legacy Groq-history keys and visit personalisation; it intentionally does not delete independent journals or coping-tool settings. The button names that scope.

Old shared IndexedDB records cannot be assigned reliably to a new session, so the new app never imports them and requests deletion of the old `relevia` database. Blocked/error callbacks produce a retry message, rather than reporting success. Delete-all broadcasts an invalidation signal to other new-version tabs when BroadcastChannel is available. Old app versions, browser suspension and missing BroadcastChannel remain reasons to test deletion across real tabs and close old tabs before declaring removal complete.

Automated tests verify stale writes, name deletion, per-session deletion, whole-chat key removal, consent withdrawal and blocked legacy deletion. Real browser transaction behaviour is not simulated by a complete IndexedDB implementation: the tests exercise the explicit callback contract. This limitation matters when interpreting the deletion claim.

## D008 — Sensitive context disables saving, not just one row

The crisis baseline still runs before model inference. A matched crisis input is held in memory and marks the entire chat sensitive. Saving is disabled and its previous saved copy is removed where storage is available. Later messages cannot silently re-enable saving, because generated replies may repeat earlier sensitive context even when their own words do not match a detector. A new cleared session is required before saving can be selected again.

This is more conservative than filtering only the matching user turn. It does not make the regex semantically reliable: the original false negatives and false alarms remain. Default non-persistence protects even undetected sensitive messages from this app's chat-storage path, but explicit saving may retain sensitive material the detector misses. The UI states this. Detection and clinical-content improvements are separate evaluation tasks.

## D009 — Remove secondary disclosure paths

The Home letter no longer reads chat history, stored names or visit counters. Its grounding content remains. `releviaBrain.js` and `Chatbot.jsx` no longer log user messages, names, emotional-tone labels or response prefixes. `ErrorBoundary.jsx` no longer persists error messages, stacks or URLs, since exceptions may contain user content. Its reusable helpers were moved to a separate module to preserve the changed-file lint gate. Existing old error records are not automatically interpreted as safe; a whole-site storage review remains necessary.

Speech starts disabled and the privacy disclosure distinguishes browser voice services from local model inference. Analytics, model downloads, journals and visualization settings remain separate data flows. The retired Groq module is a throwing stub with no key access or network request; its prior implementation remains in Git. No credential was deleted or rotated.

## Storage inventory and residual scope

| Owner | Storage | Milestone treatment |
|---|---|---|
| Chat service | Memory; opted-in bounded localStorage snapshots | Replaced shared default persistence; tested |
| Old chat service | IndexedDB `relevia` | Never imported; deletion requested and failure reported |
| Old Groq service | `relevia_memory_*` | No active implementation; delete-all removes legacy keys |
| Home letter | `relevia_visits`, session visit counter | New implementation no longer reads/writes; chat deletion removes legacy values |
| Journaling component | journalDraft, journalEntries, customPrompts, journalSettings | Inspected; existing separate journal behaviour retained; chat deletion explicitly excludes it |
| Visualization component | completion count, theme and personal settings | Inspected; separate preferences retained |
| Error boundary | old `error_*` entries | New writes removed; historical records require separate site-data cleanup |

The engineering benefit is a smaller default retention surface and explicit failure semantics. The research benefit is that model comparisons no longer silently inherit another session's history. Neither benefit implies clinical effectiveness or universal privacy.
