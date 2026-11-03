# side_by_side.py - "should I ship my fine-tune to the app?" check.
#
# Run after generating the same test set with two conditions, e.g.:
#   python src/generate.py --model configs/models/llama-3.2-3b.yaml --condition tuned_prompt --testset val --limit 40
#   python src/generate.py --model configs/models/llama-3.2-3b.yaml --condition finetuned    --testset val --limit 40
#   python src/side_by_side.py --model llama-3.2-3b --a tuned_prompt --b finetuned --testset val
#
# Writes results/side_by_side_<a>_vs_<b>.md with the replies next to each other in a
# random order (A/B hidden), and a key at the bottom. I read it, pick the better reply
# for each one, and only then look at the key. Ship the fine-tune only if it clearly wins.
# (Quick check for the app - the paper uses the proper rating sheets.)

import argparse, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, read_jsonl  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--testset", default="val")
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    gen = ROOT / "results" / "generations"
    tag = args.testset.replace("/", "-")
    load = lambda c: {r["id"]: r for r in read_jsonl(gen / f"{args.model}__{c}__{tag}__seed{args.seed}.jsonl")}
    A, B = load(args.a), load(args.b)
    ids = [i for i in A if i in B]

    rng = random.Random(0)
    lines, key = [f"# {args.model}: which reply is better?\n"], []
    for n, i in enumerate(ids, 1):
        first_is_a = rng.random() < 0.5
        r1, r2 = (A[i], B[i]) if first_is_a else (B[i], A[i])
        lines += [f"## {n}", f"**User:** {A[i]['prompt']}\n", f"**Reply 1:** {r1['generated']}\n",
                  f"**Reply 2:** {r2['generated']}\n", "Better: ___\n"]
        key.append(f"{n}: 1={args.a if first_is_a else args.b}")
    lines += ["\n---\n<details><summary>Key (open after choosing)</summary>\n", "\n".join(key), "\n</details>"]

    out = ROOT / "results" / f"side_by_side_{args.a}_vs_{args.b}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ {len(ids)} pairs -> {out}")


if __name__ == "__main__":
    main()
