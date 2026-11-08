# Browser benchmark v1 (Intel integrated GPU, before any Windows GPU change)

Run 8 November 2026, 17:11 UTC, with `runBrowserBenchmark` from the application, in the Claude desktop app's built-in Chromium pane (Chrome 152, MSIX build) via the local dev server. The model was `Llama-3.2-1B-Instruct-q4f16_1-MLC`, the application's "lite" tier, already cached, under WebLLM 0.2.79. The research prompts A and B came from `configs/experiment_01.pilot.json`, with 3 alternating repeats after one warm-up.

WebGPU returned the **Intel UHD (gen-12lp)** adapter even when asked for `high-performance`. No Windows per-app GPU preference was set (`HKCU\Software\Microsoft\DirectX\UserGpuPreferences` is empty), so the RTX 4060 was not used. This is the "before" measurement. The "after" run needs the GPU preference changed for the browser executable, which is the user's decision. Changing system settings is outside what the agent may do.

| | A | B |
|---|---|---|
| median TTFT | 1.03 s | 2.44 s |
| median end-to-end | 7.42 s | 8.81 s |
| runtime decode | 5.63 tok/s | 5.67 tok/s |
| runtime prefill | 77 tok/s | 83 tok/s |
| effective output | 4.85 tok/s | 4.08 tok/s |
| failures | 0/3 | 0/3 |

Startup (cached): 4.56 s. Unload: 0.39 s. Model switching was not measured.

B's longer system prompt (202 vs 79 prompt tokens) costs about 1.4 s more before the first token, which matches the CPU finding in notebook 07. Decoding speed is the same. The model files are referenced by mutable `main` URLs, so they are not checksummed. With only 3 repeats on one machine, these numbers describe this laptop, not browsers in general. A different model (1B Llama) was used from the Python experiments (1.5B Qwen), so the two are not comparable.
