# Table 3. LoRA smoke test (pipeline check, not a result)

Generated from `results/lora/smoke-v1/manifest.json`.

| Field | Value |
|---|---|
| `mode` | `"smoke"` |
| `model_revision` | `"989aa7980e4cf806f80c7fef2b1adb7bc71aa306"` |
| `learning_rate` | `0.0002` |
| `settings` | `{"train_rows": 16, "val_rows": 8, "max_length": 256, "max_steps": 4, "grad_accum": 2}` |
| `train_rows` | `16` |
| `train_groups` | `9` |
| `val_rows` | `8` |
| `val_groups` | `4` |
| `train_examples` | `15` |
| `val_examples` | `7` |
| `trainable_parameters` | `1089536` |
| `total_parameters` | `1544803840` |
| `val_loss_before` | `4.019613888684441` |
| `val_loss_after` | `3.6654850847580853` |
| `training_seconds` | `176.51726369990502` |
| `rss_after_training_bytes` | `7251238912` |
| `adapter_bytes` | `4378942` |
| `device` | `"cpu"` |
| `torch` | `"2.8.0+cpu"` |
| `peft` | `"0.17.1"` |
| `final_test_read` | `false` |
