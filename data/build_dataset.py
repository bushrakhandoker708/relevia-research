# build_dataset.py - turns EmpatheticDialogues into my train/val/test files.
#
# Run:  python data/build_dataset.py
#
# Output (data/processed/):
#   train.jsonl        official train split, seen emotions only      -> fine-tuning
#   val.jsonl          official valid split, seen emotions only      -> prompt tuning, early checks
#   fewshot.jsonl      k examples from val, used in the tuned prompt
#   test_seen.jsonl    official test split, seen emotions            -> in-distribution test
#   test_unseen.jsonl  official test split, HELD-OUT emotions only   -> "unseen scenarios" (RQ1)
#   split_info.json    counts + settings, goes straight into the paper
#
# Why I do it this way:
#   - Official splits (Rashkin et al. 2019) are split by the speaker who wrote the situation,
#     so nobody's story leaks from train into test. My old script only read train.csv.
#   - Held-out emotions are removed from train AND val, so neither fine-tuning nor
#     prompt tuning ever sees them.
#   - valid.csv / test.csv have an extra 9th column (retrieval distractors) that ISN'T
#     in the header. A plain DictReader treats ~half of those rows as broken. I just
#     keep the first 8 columns. Only a handful of rows are truly broken (<8 columns).

import csv, json, random, sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from common import ROOT, write_jsonl  # noqa: E402

import yaml

sys.stdout.reconfigure(encoding="utf-8")
cfg = yaml.safe_load(open(ROOT / "configs" / "base.yaml", encoding="utf-8"))["data"]
RAW = ROOT / cfg["raw_dir"]
OUT = ROOT / cfg["processed_dir"]
HELDOUT = set(cfg["heldout_emotions"])
COLS = ["conv_id", "utterance_idx", "context", "prompt", "speaker_idx", "utterance", "selfeval", "tags"]


def clean(text):
    # ED writes commas as _comma_ so their CSV doesn't break
    return text.replace("_comma_", ",").strip()


def read_split(name):
    convs, broken = defaultdict(list), 0
    with open(RAW / f"{name}.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            if len(row) < 8 or not row[1].isdigit():
                broken += 1
                continue
            convs[row[0]].append(dict(zip(COLS, row[:8])))
    return convs, broken


def to_pairs(convs):
    pairs = []
    for conv_id, turns in convs.items():
        turns.sort(key=lambda t: int(t["utterance_idx"]))
        emotion = turns[0]["context"]
        situation = clean(turns[0]["prompt"])
        # odd turns = person sharing, even turns = listener. I only use listener replies as targets.
        for i, (prev, cur) in enumerate(zip(turns, turns[1:])):
            if int(cur["utterance_idx"]) % 2 != 0:
                continue
            # earlier turns, so a turn-4 reply isn't judged without the turns it answers
            history = [{"role": "user" if int(t["utterance_idx"]) % 2 else "assistant",
                        "content": clean(t["utterance"])} for t in turns[:i]]
            user_msg, reply = clean(prev["utterance"]), clean(cur["utterance"])
            # NOTE: I used to glue the situation onto the first message, but the first
            # message usually retells it ("My cat has cancer... I found out my cat has
            # cancer"). Real users don't type that, so I keep it in its own field.
            if len(reply.split()) < cfg["min_reply_words"] or len(user_msg.split()) < cfg["min_prompt_words"]:
                continue
            if reply.lower() == user_msg.lower():
                continue
            pairs.append({
                "id": f"{conv_id}_t{cur['utterance_idx']}",
                "conv_id": conv_id,
                "emotion": emotion,
                "turn": int(cur["utterance_idx"]),
                "situation": situation,
                "history": history,
                "prompt": user_msg,
                "response": reply,
            })
    return pairs


def download_if_missing():
    # data/raw is gitignored, so on Colab / a fresh clone I fetch the official release
    if (RAW / "train.csv").exists():
        return
    import io, requests, tarfile
    print("Downloading EmpatheticDialogues...")
    r = requests.get("https://dl.fbaipublicfiles.com/parlai/empatheticdialogues/empatheticdialogues.tar.gz")
    r.raise_for_status()
    with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:gz") as tar:
        tar.extractall(RAW.parent, filter="data")


def main():
    random.seed(42)
    download_if_missing()
    info = {"heldout_emotions": sorted(HELDOUT), "broken_rows": {}}

    splits = {}
    for name in ["train", "valid", "test"]:
        convs, broken = read_split(name)
        info["broken_rows"][name] = broken
        splits[name] = to_pairs(convs)

    seen = lambda rows: [r for r in rows if r["emotion"] not in HELDOUT]
    unseen = lambda rows: [r for r in rows if r["emotion"] in HELDOUT]

    train, val = seen(splits["train"]), seen(splits["valid"])
    test_seen, test_unseen = seen(splits["test"]), unseen(splits["test"])

    # few-shot examples for the tuned prompt: first-turn pairs from val, different emotions
    random.shuffle(val)
    fewshot, used = [], set()
    for r in val:
        if r["turn"] == 2 and r["emotion"] not in used and 8 <= len(r["response"].split()) <= 40:
            fewshot.append(r)
            used.add(r["emotion"])
        if len(fewshot) == cfg["fewshot_k"]:
            break
    fewshot_ids = {r["id"] for r in fewshot}
    val = [r for r in val if r["id"] not in fewshot_ids]  # never evaluate on my own examples

    # sanity checks - fail loudly if something leaked
    assert not HELDOUT & {r["emotion"] for r in train + val}, "held-out emotion leaked into train/val"
    assert not {r["conv_id"] for r in train} & {r["conv_id"] for r in test_seen + test_unseen}, "conv leak"

    for name, rows in [("train", train), ("val", val), ("fewshot", fewshot),
                       ("test_seen", test_seen), ("test_unseen", test_unseen)]:
        random.shuffle(rows)
        write_jsonl(OUT / f"{name}.jsonl", rows)
        info[name] = {"pairs": len(rows), "conversations": len({r["conv_id"] for r in rows})}
        print(f"{name:12s} {len(rows):6d} pairs")

    info["test_unseen_by_emotion"] = dict(Counter(r["emotion"] for r in test_unseen))
    with open(OUT / "split_info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    print("broken rows skipped:", info["broken_rows"])
    print(f"✅ wrote {OUT}")


if __name__ == "__main__":
    main()
