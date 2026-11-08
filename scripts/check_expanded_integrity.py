"""Check group and text separation; lexical similarity is not semantic proof."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def normal(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))


def audit():
    path = ROOT / 'data/experiment_01_expanded/test.jsonl'
    rows = read(path)
    prior = read(ROOT / 'data/experiment_01/dev.jsonl') + read(ROOT / 'data/experiment_01/test.jsonl')
    assert len(rows) == len({r['conversation_group_id'] for r in rows}) == 60
    assert not {r['conversation_group_id'] for r in rows} & {r['conversation_group_id'] for r in prior}
    texts = [normal(r['input_text']) for r in rows]
    assert len(set(texts)) == len(texts)
    candidates = [(r['scenario_id'], r['input_text']) for r in prior]
    fewshot = ROOT / 'data/processed/fewshot.jsonl'
    assert fewshot.exists(), 'The original few-shot partition is required for this audit'
    candidates += [(f'fewshot-{i}', r['prompt']) for i, r in enumerate(read(fewshot))]
    assert not set(texts) & {normal(t) for _, t in candidates}
    flagged = []
    for i, row in enumerate(rows):
        left = set(normal(row['input_text']).split())
        comparisons = candidates + [(r['scenario_id'], r['input_text']) for r in rows[:i]]
        for ident, text in comparisons:
            right = set(normal(text).split())
            score = len(left & right) / len(left | right)
            if score >= 0.65:
                flagged.append({'left': row['scenario_id'], 'right': ident, 'jaccard': score})
    report = {'scenarios': len(rows), 'unique_groups': len(rows), 'exact_overlap': 0,
              'near_duplicate_threshold': 0.65, 'near_duplicate_candidates': flagged,
              'fewshot_count': len(read(fewshot)), 'human_review': 'unavailable',
              'limitations': 'Token Jaccard cannot exclude semantic overlap or pretraining contamination.',
              'data_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    assert not flagged, 'Review lexical near-duplicate candidates before freezing'
    return report


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
