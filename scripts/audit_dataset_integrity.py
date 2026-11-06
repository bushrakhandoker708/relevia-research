"""Metadata-only provenance and duplication audit; quarantined text is never exported."""
import collections
import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normal(text):
    return ' '.join(text.replace('_comma_', ',').casefold().split())


def read(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def main():
    blocked = json.loads((ROOT / 'data/quarantine_manifest.json').read_text())['blocked'][0]
    path = ROOT / blocked['path']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != blocked['sha256']:
        raise ValueError('Quarantine artifact changed')
    archive = read(path)
    pairs = collections.Counter((normal(x['prompt']), normal(x['response'])) for x in archive)
    prompts = collections.Counter(normal(x['prompt']) for x in archive)
    report = {'quarantine': {'path': blocked['path'], 'sha256': digest, 'rows':len(archive),
              'duplicate_pair_rows':sum(n-1 for n in pairs.values()), 'duplicate_prompt_rows':sum(n-1 for n in prompts.values()),
              'rows_with_escaped_comma':sum('_comma_' in x['prompt'] or '_comma_' in x['response'] for x in archive)},
              'limits':'Normalised exact matches only; no proof of consent, complete provenance, semantic independence or absence of pretraining contamination.'}
    raw_matches = {}
    for p in (ROOT / 'data/raw').rglob('*.csv'):
        situations, utterances = set(), set()
        with p.open(encoding='utf-8', newline='') as f:
            for row in csv.DictReader(f):
                situations.add(normal(row.get('prompt') or ''))
                utterances.add(normal(row.get('utterance') or ''))
        raw_matches[p.relative_to(ROOT).as_posix()] = {
            'archive_prompt_rows_matching_situation':sum(normal(x['prompt']) in situations for x in archive),
            'archive_response_rows_matching_utterance':sum(normal(x['response']) in utterances for x in archive),
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    report['source_similarity_not_provenance'] = raw_matches
    splits = {n:read(ROOT / f'data/processed/{n}.jsonl') for n in ['train','dev','fewshot','val','test_seen','test_unseen']}
    pair_sets = {n:{(normal(x['prompt']),normal(x['response'])) for x in rows} for n,rows in splits.items()}
    report['active_normalised_pair_intersections'] = {a+'__'+b:len(pair_sets[a]&pair_sets[b]) for a,b in itertools.combinations(splits,2)}
    report['archive_pair_matches_active'] = {n:len(set(pairs)&s) for n,s in pair_sets.items()}
    fewshot_inputs = {normal(x['prompt']) for x in splits['fewshot']}
    report['fewshot_input_intersections'] = {n:len(fewshot_inputs & {normal(x['prompt']) for x in splits[n]})
                                            for n in ['val','test_seen','test_unseen']}
    if any(report['fewshot_input_intersections'].values()):
        raise ValueError('Few-shot input text overlaps validation or test')
    report['active_counts'] = {n:len(rows) for n,rows in splits.items()}
    out = ROOT/'results/milestone_3/dataset_integrity.json';out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
