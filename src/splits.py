"""Conversation-level partitions; no model/prompt development on validation/test."""
import itertools
import random


def assert_disjoint(splits):
    for a, b in itertools.combinations(splits, 2):
        overlap = {r['conv_id'] for r in splits[a]} & {r['conv_id'] for r in splits[b]}
        if overlap:
            raise ValueError(f'{a}/{b}: {len(overlap)} overlapping conversation groups')


def reserve_development(train, validation, fewshot_k=4, seed=42):
    rng = random.Random(seed)
    groups = sorted({r['conv_id'] for r in train})
    rng.shuffle(groups)
    dev_groups = set(groups[:max(1, len(groups) // 10)])
    development = sorted((r for r in train if r['conv_id'] in dev_groups), key=lambda r: r['id'])
    rng.shuffle(development)
    examples, emotions = [], set()
    for row in development:
        if row['turn'] == 2 and row['emotion'] not in emotions and 8 <= len(row['response'].split()) <= 40:
            examples.append(row); emotions.add(row['emotion'])
        if len(examples) == fewshot_k:
            break
    if len(examples) != fewshot_k:
        raise ValueError('Insufficient eligible development conversations')
    example_groups = {r['conv_id'] for r in examples}
    result = {
        'train': [r for r in train if r['conv_id'] not in dev_groups],
        'dev': [r for r in development if r['conv_id'] not in example_groups],
        'fewshot': examples,
        'val': validation,
    }
    assert_disjoint(result)
    return result
