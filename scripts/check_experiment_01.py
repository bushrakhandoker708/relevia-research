"""Fail closed on changed pilot inputs, cross-split groups or copied prompts."""
import json
from experiment_01 import ROOT, sha, load_rows, check_pair


def main():
    dev = load_rows(ROOT/'data/experiment_01/dev.jsonl', 'dev')
    test = load_rows(ROOT/'data/experiment_01/test.jsonl', 'test')
    check_pair(dev, test)
    freeze = json.loads((ROOT/'configs/experiment_01.freeze.json').read_text())
    paths = {'config':ROOT/'configs/experiment_01.pilot.json', 'dev':ROOT/'data/experiment_01/dev.jsonl', 'test':ROOT/'data/experiment_01/test.jsonl',
             'rubric':ROOT/'docs/experiment_01_rubric.md', 'runner':ROOT/'scripts/experiment_01.py'}
    for name,path in paths.items():
        if sha(path) != freeze[name+'_sha256']: raise ValueError('Frozen input changed: '+name)
    cfg = json.loads(paths['config'].read_text())
    for row in test:
        for prompt in cfg['prompts'].values():
            if row['input_text'].casefold() in prompt.casefold(): raise ValueError('Test input copied into prompt')
    report = {'dev_rows':len(dev),'test_rows':len(test),'group_overlap':0,'normalised_input_overlap':0,
              'fewshot_examples':0,'frozen_hashes_verified':True,'limitations':'No semantic independence or pretraining contamination guarantee.'}
    out=ROOT/'results/milestone_3/experiment_leakage.json';out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__ == '__main__': main()
