"""Deterministic metadata-only leakage report. Fails on cross-partition groups."""
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from splits import assert_disjoint


def main():
    blobs = {name: (ROOT / f'data/processed/{name}.jsonl').read_bytes()
             for name in ['train', 'dev', 'fewshot', 'val', 'test_seen', 'test_unseen']}
    splits = {name: [json.loads(line) for line in data.decode('utf-8').splitlines() if line.strip()] for name, data in blobs.items()}
    report = {'dataset_version': 'ed-group-v2', 'seed': 42,
              'counts': {k: len(v) for k, v in splits.items()},
              'overlap': {a + '__' + b: len({r['conv_id'] for r in splits[a]} & {r['conv_id'] for r in splits[b]})
                          for a, b in itertools.combinations(splits, 2)},
              'sha256': {k: hashlib.sha256(blobs[k]).hexdigest() for k in splits}}
    out = ROOT / 'results/milestone_2/leakage.json'; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    assert_disjoint(splits)
    before = ROOT / 'results/milestone_2/leakage-before.json'
    if before.exists():
        expected = json.loads(before.read_text())['test_hashes']
        for name, checksum in expected.items():
            if report['sha256'][name] != checksum:
                raise ValueError(f'Frozen test bytes changed: {name}')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
