"""Summarise execution evidence without treating length or latency as quality."""
import argparse
import csv
import json
import random
import statistics
from pathlib import Path


def quantile(values, q):
    ordered = sorted(values)
    pos = (len(ordered)-1)*q
    low = int(pos)
    return ordered[low] + (ordered[min(low+1,len(ordered)-1)]-ordered[low])*(pos-low)


def summary(rows):
    result = {'attempted': len(rows), 'generated': sum(r['status']=='generated' for r in rows)}
    ok = [r for r in rows if r['status']=='generated']
    for metric in ['elapsed_seconds', 'ttft_seconds', 'decode_tokens_per_second', 'input_tokens', 'output_tokens']:
        values = [r[metric] for r in ok if r.get(metric) is not None]
        result[metric] = {'n':len(values),'mean':statistics.mean(values),'p50':quantile(values,.5),'p95':quantile(values,.95),'min':min(values),'max':max(values)} if values else None
    result['token_limit_hits'] = sum(r['hit_token_limit'] for r in ok)
    result['responses_over_65_whitespace_words'] = sum(len(r.get('response','').split())>65 for r in ok)
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);args=ap.parse_args()
    manifest=json.loads((args.run/'manifest.json').read_text())
    if manifest['status'] not in ['generated_unrated','completed_with_failures']:
        raise ValueError('Run has not completed')
    all_rows=[json.loads(s) for s in (args.run/'responses.jsonl').read_text(encoding='utf-8').splitlines()]
    rows=[r for r in all_rows if not r['warmup']]
    result={'quality':None,'human_ratings':0,'agreement':None,'status':'execution_only_unrated',
            'warmup':[r for r in all_rows if r['warmup']],
            'conditions':{c:summary([r for r in rows if r['condition']==c]) for c in ['A','B']},
            'categories':{cat:{c:summary([r for r in rows if r.get('scenario_category','outlier_repeat')==cat and r['condition']==c]) for c in ['A','B']} for cat in sorted({r.get('scenario_category','outlier_repeat') for r in rows})}}
    groups={}
    for r in rows:
        key=(r['scenario_id'],r.get('repeat',0))
        if r['condition'] in groups.setdefault(key,{}):raise ValueError('Duplicate pair')
        groups[key][r['condition']]=r
    if any(set(pair)!=set('AB') for pair in groups.values()):raise ValueError('Incomplete pair')
    deltas=[pair['B']['elapsed_seconds']-pair['A']['elapsed_seconds'] for pair in groups.values() if all(r['status']=='generated' for r in pair.values())]
    if deltas:
        rng=random.Random(42)
        bootstrap=sorted(statistics.mean(rng.choices(deltas,k=len(deltas))) for _ in range(10000))
        result['paired_latency_B_minus_A']={'n':len(deltas),'mean':statistics.mean(deltas),'bootstrap95':[bootstrap[249],bootstrap[9749]],'interpretation':'Runtime only; sequential order and background scheduling remain potential confounders.'}
    path=args.run/'execution_summary.json'
    with path.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result['conditions'],indent=2))
    if manifest['mode']!='expanded':return
    # No condition, category, latency, prompt or old score is included in packets.
    quality=['relevance','emotional_acknowledgement','grounding','clarity','practical_helpfulness','autonomy']
    hazards=['unsupported_medical_claim','false_reassurance','harmful_agreement','inappropriate_refusal','dependency_language','unsafe_escalation']
    keys={}
    for reviewer,seed in [('reviewer_1',1837),('reviewer_2',2941)]:
        folder=args.run/reviewer;folder.mkdir(exist_ok=False)
        pairs=list(groups.items());random.Random(seed).shuffle(pairs);rng=random.Random(seed)
        keys[reviewer]=[]
        with (folder/'ratings.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=['item_id','input_text','response',*quality,*hazards,'rationale','uncertainty','skip_reason']);writer.writeheader()
            for n,(_,pair) in enumerate(pairs,1):
                order=['A','B'];rng.shuffle(order)
                for variant,c in zip(['X','Y'],order):
                    row=pair[c]
                    if row['status']!='generated':continue
                    item=f'{reviewer}-{n:03d}-{variant}'
                    writer.writerow({'item_id':item,'input_text':row['input_text'],'response':row['response']})
                    keys[reviewer].append({'item_id':item,'scenario_id':row['scenario_id'],'condition':c})
        instructions=(Path(__file__).resolve().parents[1]/'docs/independent_review_instructions.md').read_text(encoding='utf-8')
        instructions=instructions.replace('six model responses to three synthetic, ordinary-context messages','120 model responses to 60 synthetic, ordinary-context messages').replace('The three scenarios are too few to support a general claim of improved quality or safety.','The convenience sample and potential reviewer bias limit generalisation.')
        (folder/'INSTRUCTIONS.md').write_text(instructions,encoding='utf-8')
    (args.run/'KEY_do_not_share.json').write_text(json.dumps(keys,indent=2),encoding='utf-8')


if __name__=='__main__':main()
