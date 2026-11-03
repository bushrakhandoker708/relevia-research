# dataset.py - builds empathy_42k.jsonl for the Relevia LoRA
#
# FIXED (v2). What was broken in my first version:
#   1. I paired the `prompt` column (the speaker's *situation* description) with a
#      RANDOM `utterance` from anywhere in the conversation. So "My cat passed away"
#      got matched with "Yes I think so, he was all grey and stuff" and in a lot of
#      rows the "response" was literally the speaker re-telling their own story.
#      Now I walk each conversation in order and only keep
#      (speaker turn -> listener reply) pairs, which is what the dataset is meant for.
#   2. EmpatheticDialogues escapes commas as "_comma_". I never decoded them, so the
#      model was learning to write "Hey_comma_ we all pig out". Decoded now.
#   3. The "mental_health_conversations" and "crisis_counseling_60k" URLs don't exist
#      on HuggingFace (they 404), so both silently failed and I only ever got 15k
#      ED rows, not 42k. I swapped in a counselling set that actually exists and
#      dropped the fake crisis one.
#   4. 5 rows in train.csv have extra commas in them and break the column layout.
#      I skip those instead of crashing / reading shifted columns.

import csv, json, random, requests, tarfile, io, os, sys
from collections import defaultdict

# Windows console is cp1252 and the ✅ print at the end crashed the whole script
sys.stdout.reconfigure(encoding="utf-8")

random.seed(42)
OUT_FILE = "empathy_42k.jsonl"
ED_DIR = "tmp_ed/empatheticdialogues"

def clean(text):
    # ED uses _comma_ instead of real commas so their CSV doesn't break
    return text.replace("_comma_", ",").strip()

def good_pair(prompt, response):
    # throw away junk: super short replies ("lol", "yes") and replies that just
    # parrot the prompt back, those teach the model nothing about empathy
    if len(response.split()) < 4 or len(prompt.split()) < 3:
        return False
    if response.lower() == prompt.lower():
        return False
    return True

# ---------- 1. EmpatheticDialogues ----------
if not os.path.exists(f"{ED_DIR}/train.csv"):
    print("Downloading EmpatheticDialogues...")
    r1 = requests.get("https://dl.fbaipublicfiles.com/parlai/empatheticdialogues/empatheticdialogues.tar.gz")
    r1.raise_for_status()
    with tarfile.open(fileobj=io.BytesIO(r1.content), mode='r:gz') as tar:
        tar.extractall("tmp_ed", filter='data')
else:
    print("EmpatheticDialogues already downloaded, reusing tmp_ed/")

# group rows by conversation so I can read turns in the right order
convs = defaultdict(list)
skipped = 0
with open(f"{ED_DIR}/train.csv", newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        # broken rows get extra keys (None) from DictReader, skip them
        if None in row or not row.get("utterance_idx", "").isdigit():
            skipped += 1
            continue
        convs[row["conv_id"]].append(row)

emp_all = []
for conv_id, turns in convs.items():
    turns.sort(key=lambda t: int(t["utterance_idx"]))
    situation = clean(turns[0]["prompt"])
    # turn 1 = the person sharing their feelings, turn 2 = the listener replying, etc.
    # I only want listener replies as targets (even utterance_idx).
    for prev, cur in zip(turns, turns[1:]):
        if int(cur["utterance_idx"]) % 2 != 0:
            continue
        user_msg = clean(prev["utterance"])
        reply = clean(cur["utterance"])
        # on the first exchange I give the situation as extra context, it's what
        # the speaker is actually going through
        if int(prev["utterance_idx"]) == 1 and situation and situation.lower() not in user_msg.lower():
            user_msg = f"{situation} {user_msg}"
        if good_pair(user_msg, reply):
            emp_all.append({"prompt": user_msg, "response": reply, "source": "empathetic_dialogues"})

random.shuffle(emp_all)
emp = emp_all[:30000]
print(f"Extracted {len(emp)} pairs from EmpatheticDialogues (skipped {skipped} broken rows)")

# ---------- 2. Mental Health Counseling Conversations ----------
# real dataset: counsellor answers to real questions (~3.5k rows, so I take all of them)
# it's gated, so accept the terms on its HF page and run `huggingface-cli login` first
print("Downloading Mental-Health-Counseling-Conversations...")
mhc = []
try:
    from datasets import load_dataset
    ds = load_dataset("Amod/mental_health_counseling_conversations", split="train")
    for x in ds:
        p, r = (x.get("Context") or "").strip(), (x.get("Response") or "").strip()
        if good_pair(p, r):
            mhc.append({"prompt": p, "response": r, "source": "counseling"})
    print(f"Extracted {len(mhc)} rows from Mental Health Counseling Conversations")
except Exception as e:
    # not fatal, I can still train on ED alone
    print(f"Error with Mental Health Counseling Conversations: {e}")

# ---------- 3. Merge ----------
all_data = emp + mhc
random.shuffle(all_data)

# ---------- 4. Save ----------
with open(OUT_FILE, "w", encoding='utf-8') as f:
    for item in all_data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"✅ Saved {len(all_data)} rows → {OUT_FILE}")
print(f"Distribution: EmpatheticDialogues={len(emp)}, Counseling={len(mhc)}")
