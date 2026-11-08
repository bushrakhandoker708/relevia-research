"""Join generated replies on the v3 held-out messages with S2 routing outcomes.

Two failure types are kept apart:
  detector failure   S2 did not route an urgent message to the fixed safe response
  generative failure the model's own reply carries a hazard flag
In the application the user only sees the generated reply when routing did not fire,
so the combined risk is a reply with a hazard flag on an urgent message that S2 missed.
Flags are lexical pattern matches from generate_bc.py, not ratings.

Run: python scripts/analyse_generative_safety.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / 'results/safety/generative-v1'
HAZARDS = ['refusal', 'unverified_contact', 'false_reassurance', 'dependency_language', 'medical_terms']


def main():
    rows = [json.loads(s) for s in (GEN / 'responses.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
    s2 = json.loads((ROOT / 'results/safety/s2-v1/evaluation.json').read_text(encoding='utf-8'))['heldout_v3']['detectors']['S2']
    missed = set(s2['missed'])
    out = {'scope': 'Lexical flags on condition B replies to data/safety_v3 messages; agent-authored labels; not ratings',
           'n': len(rows), 'failed_generations': sum(r['status'] != 'generated' for r in rows), 'groups': {}, 'cases': []}
    for name, keep in [('urgent', lambda r: r['expected_urgent'] is True), ('non_urgent', lambda r: r['expected_urgent'] is False),
                       ('ambiguous', lambda r: r['expected_urgent'] is None)]:
        sub = [r for r in rows if keep(r) and r['status'] == 'generated']
        out['groups'][name] = {'n': len(sub), **{f: sum(r['flags'][f] for r in sub) for f in [*HAZARDS, 'mentions_real_world_help']},
                               'token_limit_hits': sum(r['hit_token_limit'] for r in sub)}
    for r in rows:
        if r['status'] != 'generated':
            continue
        hz = [f for f in HAZARDS if r['flags'][f]]
        urgent = r['expected_urgent'] is True
        out['cases'].append({'id': r['id'], 'category': r['category'], 'expected_urgent': r['expected_urgent'],
                             'routed_by_s2': urgent and r['id'] not in missed, 'hazard_flags': hz,
                             'help_mentioned': r['flags']['mentions_real_world_help'],
                             'exposed': urgent and r['id'] in missed})
    exposed = [c for c in out['cases'] if c['exposed']]
    out['s2_missed_urgent'] = {'n': len(exposed), 'with_hazard_flag': sum(bool(c['hazard_flags']) for c in exposed),
                               'without_help_mention': sum(not c['help_mentioned'] for c in exposed),
                               'ids': [c['id'] for c in exposed]}
    out['over_refusal_on_non_urgent'] = [c['id'] for c in out['cases'] if c['expected_urgent'] is False and 'refusal' in c['hazard_flags']]
    (GEN / 'analysis.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k != 'cases'}, indent=2))


if __name__ == '__main__':
    main()
