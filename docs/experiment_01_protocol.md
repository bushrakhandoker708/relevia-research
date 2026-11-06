# Experiment 01: controlled prompting pilot

I want to establish whether changing the prompt improves supportive responses before adding trainable parameters. The research question is: does a developed prompt improve quality over a minimal safe prompt when the underlying model is unchanged? A useful result may be a failure to improve; neither a longer prompt nor a successful generation is evidence of quality.

## Model and environment decision

The requested preference was Llama-3.2-1B-Instruct, whose public metadata identifies revision `9213176726f574b556790deb65791e0c5aa438b6` and manual gated access. It was not cached locally. The available runtime is PyTorch 2.8.0+cpu with Transformers 4.56.2 and no CUDA. Rather than claiming the preferred model ran, this pilot uses the publicly accessible [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) at revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, whose pinned licence is Apache-2.0. This is an implementation choice based on access and compatibility, not evidence that Qwen is a better supportive model. The download is about 3.09 GB of weights and is excluded from Git.

Larger models and LoRA are deferred because they would introduce resource and treatment changes before the prompting baseline is understood. The old app’s MLC weights are a different runtime artifact, not interchangeable Transformers weights. A later Llama replication would be a new experiment, not a renamed Qwen result.

## Treatments and development

A and B share the same minimal safety instructions. B adds situation-specific acknowledgement, a distinction between emotions and harmful beliefs, optional practical help and autonomy. Four synthetic development cases are used for prompt review. The first actual run showed truncation and unsupported inferences. B was revised to 2–4 complete sentences, at most 65 words, no lists/placeholders and no invented details. The second run evaluates that candidate on development only. The prompt log records the actual decision and remaining failures.

The test dataset is authored after development review, then the configuration, development file, test file, rubric and runner are SHA-256 locked before test generation. No test outputs inform prompt revision. This is a small agent-authored held-out pilot, not an independently curated benchmark. There are no few-shot examples. New prompt changes after inspecting test outcomes require a new version and fresh evaluation data.

## Controls and execution

Both conditions use identical model/tokenizer revision, CPU float32, eight threads, greedy decoding, seed 42, a 110-token maximum and the same inputs. The runner reuses one model in evaluation mode without conversation history or adapter training. A/B order is seeded and randomised within each scenario. Longer system prompts are part of the treatment; elapsed-time differences therefore cannot be interpreted as pure generation-speed effects.

Only the synthetic experiment directory is accepted. Source, split, review status, unique IDs, cross-split group separation and normalised duplicate inputs are checked. Frozen inputs are checked before test loading. Outputs are appended and flushed with failure status, elapsed seconds, token counts and token-limit indicators. A new output directory is required, so reruns cannot silently overwrite results. Null ratings are missing evidence.

The initial development load attempted optional network metadata queries despite `local_files_only`. Subsequent runs set Hugging Face and Transformers offline flags before imports. The public model download used network access; conversation generation itself uses local weights. The model’s inherited sampling settings cause warnings under greedy decoding and are not evidence of sampling. Runtime configuration and overrides are retained for the frozen test run.

## Evaluation

The [rubric](experiment_01_rubric.md) specifies relevance as the primary quality dimension, with emotional acknowledgement, clarity, practical helpfulness and autonomy reported separately. Six safety hazards remain separate from quality. The initial review is explicitly unblinded coding-agent review, not human evaluation. Report paired B−A differences and 10,000-resample group bootstrap intervals, without significance or clinical claims. Small samples and systematic reviewer bias limit these intervals.

The runner records outputs; `analyse_experiment_01.py` calculates diagnostics and, only when supplied explicit validated ratings, paired quality estimates. No lexical metric is called empathy or safety. Failures, token-limit hits and questionable cases remain visible even when average ratings improve. The detailed notebook includes real outputs, figures, limitations and unresolved questions.

## Gates

The browser-verification exception is accepted for local research only. Public release still requires browser and content review. The historical archive remains quarantined. This pilot must be reviewed and approved by Bushra before any LoRA training, learned routing or major UI work. An eight-case test cannot establish a production safety rate. No public push, deployment or model publication is authorised.
