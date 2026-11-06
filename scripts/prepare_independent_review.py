"""Export two blank, separately randomised packets without changing pilot evidence."""
import csv
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALITY = ['relevance', 'emotional_acknowledgement', 'grounding', 'clarity',
           'practical_helpfulness', 'autonomy']
SAFETY = ['unsupported_medical_claim', 'false_reassurance', 'harmful_agreement',
          'inappropriate_refusal', 'dependency_language', 'unsafe_escalation']
# A deliberately narrow, ordinary-context subset. Caregiving, bereavement,
# aggression, medical requests and urgent distress are excluded from this packet.
SELECTED = {'test-01', 'test-07', 'test-08'}


def main():
    source = ROOT / 'results/experiment_01/test-v1/responses.jsonl'
    rows = [json.loads(line) for line in source.read_text(encoding='utf-8').splitlines()]
    selected = [row for row in rows if row['scenario_id'] in SELECTED]
    for sid in SELECTED:
        pair = [r for r in selected if r['scenario_id'] == sid]
        if len(pair) != 2 or {r['condition'] for r in pair} != {'A', 'B'}:
            raise ValueError('Expected one complete A/B pair per scenario')
        if any(r['status'] != 'generated' for r in pair):
            raise ValueError('Cannot rate failed generations')
    out = ROOT / 'results/experiment_01/independent_review_v1'
    out.mkdir(exist_ok=False)
    keys = {}
    for reviewer, seed in [('reviewer_1', 1837), ('reviewer_2', 2941)]:
        shuffled = selected.copy()
        random.Random(seed).shuffle(shuffled)
        packet = out / reviewer
        packet.mkdir()
        with (packet / 'ratings.csv').open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'item_id', 'input_text', 'response', *QUALITY, *SAFETY,
                'rationale', 'uncertainty', 'skip_reason'])
            writer.writeheader()
            keys[reviewer] = []
            for index, row in enumerate(shuffled, 1):
                item = f'R{reviewer[-1]}-{index:03d}'
                writer.writerow({'item_id': item, 'input_text': row['input_text'],
                                 'response': row['response']})
                keys[reviewer].append({'item_id': item, 'scenario_id': row['scenario_id'],
                                       'condition': row['condition']})
        (packet / 'INSTRUCTIONS.md').write_text(
            (ROOT / 'docs/independent_review_instructions.md').read_text(encoding='utf-8'),
            encoding='utf-8')
    (out / 'KEY_do_not_share.json').write_text(json.dumps(keys, indent=2) + '\n', encoding='utf-8')
    manifest = {'status': 'prepared_reviewers_unavailable', 'human_ratings': 0,
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'scenarios': sorted(SELECTED), 'responses_per_reviewer': len(selected),
                'scope': 'pilot ordinary-context subset; not expanded independent test',
                'excluded': ['test-02', 'test-03', 'test-04', 'test-05', 'test-06'],
                'blinding_limitations': 'Style and length can reveal differences; coordinator knows conditions.'}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
