# lr_sweep.py - find the learning rate instead of guessing it.
#
# Run (Colab GPU, ~15-25 min per rate for a 3B model):
#   python src/lr_sweep.py --model configs/models/llama-3.2-3b.yaml
#
# What it does: short training runs (4,000 rows each) at several learning rates, then
# compares validation loss. The QLoRA paper (Dettmers et al. 2023) used 2e-4 for
# 7B/13B models and 1e-4 for bigger ones, so for 1-3B the sweet spot is usually
# 1e-4 to 3e-4. This checks that for MY data instead of trusting it.
#
# How I read the result:
#   - lowest val loss wins, BUT if two rates are within ~0.02 of each other I take the
#     LOWER rate (it changes the model less = less risk of the warmth/sycophancy
#     problem from the Nature 2026 paper)
#   - a rate whose val loss goes UP over training is overfitting, never pick it
# Then I put the winner in configs/base.yaml -> train.lr and do the full runs.
#
# Caveat: val loss = "how well it imitates EmpatheticDialogues replies". It's the right
# signal for picking a learning rate, but it is NOT a measure of empathy. That still
# needs the human ratings.

import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_config, adapter_dir  # noqa: E402

RATES = [5e-5, 1e-4, 2e-4, 3e-4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--rows", type=int, default=4000)
    ap.add_argument("--rates", type=float, nargs="*", default=RATES)
    args = ap.parse_args()
    cfg = load_config(args.model)

    results = []
    for lr in args.rates:
        tag = f"lr{lr:g}"
        print(f"\n===== lr = {lr:g} =====")
        subprocess.run([sys.executable, str(Path(__file__).parent / "train.py"), "--model", args.model,
                        "--seed", "1", "--limit", str(args.rows), "--lr", str(lr), "--tag", tag,
                        # ~5 checkpoints per run so I can actually see overfitting
                        "--eval-steps", str(max(10, args.rows // (cfg["train"]["batch_size"] * cfg["train"]["grad_accum"]) // 5))],
                       check=True)
        d = adapter_dir(cfg, 1)
        log = json.load(open(d.with_name(f"{d.name}_{tag}") / "train_log.json", encoding="utf-8"))
        evals = [h["eval_loss"] for h in log["history"] if "eval_loss" in h]
        results.append({"lr": lr, "best": min(evals), "final": evals[-1],
                        "overfit": len(evals) > 1 and evals[-1] > min(evals) + 0.01})

    print("\n  lr        best val   final val   overfitting?")
    for r in results:
        print(f"  {r['lr']:<9g} {r['best']:.4f}     {r['final']:.4f}      {'YES' if r['overfit'] else 'no'}")

    ok = [r for r in results if not r["overfit"]] or results
    best = min(ok, key=lambda r: r["best"])
    # prefer the lower rate when it's basically as good
    close = [r for r in ok if r["best"] - best["best"] <= 0.02]
    pick = min(close, key=lambda r: r["lr"])
    print(f"\n✅ use lr = {pick['lr']:g}  (put it in configs/base.yaml -> train.lr)")


if __name__ == "__main__":
    main()
