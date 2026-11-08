# Browser benchmark protocol

The application now contains `src/services/browserBenchmark.js`, an opt-in research harness that is not imported by the public chat. It takes an isolated engine factory, two frozen prompts and explicit model/runtime/quantisation/WASM metadata. It uses only a fixed synthetic caregiving input, records a separate warm-up and five alternating A/B repetitions, and returns a local report. It does not read chat history, contact users or upload results.

The installed WebLLM package is 0.2.79. Its local declarations support streamed completion usage. The harness records startup latency, first nonempty text-chunk latency, total response latency, reported token counts and observed output tokens per total second. Streaming chunks are not assumed to be individual tokens. GPU memory and pure prefill throughput remain null because they are not directly measured. Load and generation failures remain visible. Unit tests use an explicitly fake engine and do not count as browser measurements.

## Milestone 4 instrumentation (8 November 2026)

The harness now separates the quantities that the earlier version combined:

| Quantity | How it is recorded | Caveat |
|---|---|---|
| Startup | `startup.loadMilliseconds`, the time to first progress callback, and the caller's `cacheState` (`network_cold`, `cached` or `unknown`) | The caller must establish the cache state, for example with WebLLM's `hasModelInCache` or a fresh profile. An unlabelled state is rejected. |
| Time to first token | Wall-clock time to the first non-empty streamed chunk, plus WebLLM's own `time_to_first_token_s` | The two can differ because of worker messaging. |
| Prefill and decode | `usage.extra.prefill_tokens_per_s` and `decode_tokens_per_s` per request | These are runtime-reported counters, not GPU kernel timings. They are null if the runtime omits them. |
| End-to-end latency | Request start to stream end | Includes prefill, decoding and messaging. |
| Effective throughput | Completion tokens divided by end-to-end seconds | Deliberately lower than the decode rate. |
| Failure rate | Failed rows are kept and summarised per condition | A failed row never contributes timings. |
| Switching and unloading | Optional `switchModel` hook, then a timed `unload` | Measured once per run. |
| Hardware | `collectHardware()`: WebGPU adapter vendor, architecture, description, `shader-f16`, `maxBufferSize`, fallback flag, logical cores, `deviceMemory` | Shows the adapter the **browser** chose. On the development laptop this was Intel UHD even though an RTX 4060 is installed, so hardware must be recorded per run rather than assumed. |

The unit tests (`tests/browser-benchmark.test.js`, five tests) use a fake engine, including an injected device-lost failure. They check the bookkeeping only and are not measurements.

**First executed run (8 November 2026):** `results/performance/browser-v1-intel/`. It used the Intel integrated GPU, because Windows had no per-app GPU preference set, with Llama-3.2-1B q4f16 cached and 3 repeats. Median time to first token was 1.0 s for A and 2.4 s for B, decode was 5.6 tok/s, and there were 0/6 failures. An RTX 4060 run is pending the Windows setting.

Before execution, verify immutable converted-model and WASM artifact URLs and record their checksums. The installed model catalogue contains Qwen2.5-1.5B q4f16 and q4f32 variants, but catalogue membership does not establish that their weights are identical to the Python experiment's pinned revision. The factory must create a separate benchmark engine rather than reuse a person's chat instance. Record browser, operating system, device, cache state, power mode and concurrent activity. Do not label a cached model load a network-cold load.

Run the application locally in a disposable browser profile. Import the harness through the development server, provide the verified factory and frozen prompt strings, then save the returned JSON locally. Repeat after warm-up and in a fresh process/profile as specified by the final benchmark protocol. No public deployment is required or authorised for this check.

Browser automation was previously blocked by URL-policy support and loopback access. The accepted exception permits local research only. No new browser execution is claimed here. Missing evidence includes actual model startup, interactive chat flow, privacy lifecycle, two-tab deletion, browser cache behaviour, GPU memory and comparison with the Python backend. The current Python timings must not be presented as browser results.
