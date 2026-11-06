"""Prepare actual paired outputs for independent review; never populate ratings."""
import argparse
import csv
import json
import random
from pathlib import Path
from analyse_experiment_01 import QUALITY, SAFETY


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    rows=[json.loads(x) for x in (args.run/'responses.jsonl').read_text(encoding='utf-8').splitlines()]
    if any(x['status']!='generated' for x in rows):raise ValueError('Review failed outputs separately before export')
    groups=sorted({x['scenario_id'] for x in rows});rng=random.Random(719);rng.shuffle(groups)
    args.out.mkdir(parents=True,exist_ok=False);key=[]
    with (args.out/'blinded_rating_sheet.csv').open('w',encoding='utf-8',newline='') as f:
        fields=['item','variant','input_text','response',*QUALITY,*SAFETY,'rationale','reviewer']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for number,sid in enumerate(groups,1):
            pair=[x for x in rows if x['scenario_id']==sid]
            if len(pair)!=2 or {x['condition'] for x in pair}!={'A','B'}:raise ValueError('Incomplete or duplicate pair')
            rng.shuffle(pair)
            for variant,row in zip(['X','Y'],pair):
                item=f'item-{number:02d}'
                writer.writerow({'item':item,'variant':variant,'input_text':row['input_text'],'response':row['response']})
                key.append({'item':item,'variant':variant,'scenario_id':sid,'condition':row['condition']})
    (args.out/'KEY_do_not_share.json').write_text(json.dumps(key,indent=2)+'\n',encoding='utf-8')
    (args.out/'README.md').write_text('''# Independent review packet

The CSV contains actual synthetic-input model responses with condition labels hidden and empty rating fields. No human review has yet occurred. Use the frozen Experiment 01 rubric, including the separate safety flags. Do not send the answer key or the agent ratings to reviewers. Some synthetic cases mention grief or immediate distress; participation should be voluntary, with an appropriate reviewed study procedure before recruitment. This export does not constitute participant approval or recruitment.

Keep disagreements and uncertain ratings visible. Return completed sheets under new filenames and record reviewer provenance. This packet is prepared for the project owner; no messages or files have been sent to anyone.
''',encoding='utf-8')
    print('Prepared blank blinded ratings for',len(groups),'paired scenarios')


if __name__=='__main__':main()
