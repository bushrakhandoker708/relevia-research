"""Controlled paired base-model pilot; never trains or loads archived dialogue."""
import argparse
import hashlib
import json
import os
import platform
import random
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Transformers' optional-adapter discovery can otherwise probe the network even
# with local_files_only on the principal model load.
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_rows(path, phase):
    path = Path(path).resolve()
    if path.parent != (ROOT / 'data/experiment_01').resolve():
        raise ValueError('Only the reviewed experiment directory is allowed')
    rows = [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
    if not rows or len({x['scenario_id'] for x in rows}) != len(rows):
        raise ValueError('Missing or duplicate scenario IDs')
    for row in rows:
        if (row.get('source'), row.get('source_license'), row.get('split')) != ('synthetic', 'CC0-1.0', phase):
            raise ValueError('Unapproved source or split')
        if row.get('review_status') != 'agent_reviewed_not_clinically_validated' or not row.get('input_text', '').strip():
            raise ValueError('Missing input or documented review')
    return rows


def check_pair(dev, test):
    for field in ['scenario_id', 'conversation_group_id']:
        if {r[field] for r in dev} & {r[field] for r in test}:
            raise ValueError(f'Cross-split overlap: {field}')
    normal = lambda s: ' '.join(s.casefold().split())
    if {normal(r['input_text']) for r in dev} & {normal(r['input_text']) for r in test}:
        raise ValueError('Cross-split input duplicate')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', choices=['dev', 'test'], required=True)
    ap.add_argument('--config', type=Path, default=ROOT / 'configs/experiment_01.pilot.json')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    cfg = json.loads(args.config.read_text(encoding='utf-8'))
    import re
    if not re.fullmatch('[0-9a-f]{40}', cfg['model_revision']) or set(cfg['prompts']) != {'A', 'B'}:
        raise ValueError('Pin one model and exactly two prompts')
    if cfg['generation'] != {'max_new_tokens': 110, 'do_sample': False}:
        raise ValueError('Unexpected frozen decoding configuration')
    data = ROOT / f'data/experiment_01/{args.phase}.jsonl'
    rows = load_rows(data, args.phase)
    if args.phase == 'test':
        freeze = json.loads((ROOT / 'configs/experiment_01.freeze.json').read_text())
        for name, path in [('config', args.config), ('dev', ROOT / 'data/experiment_01/dev.jsonl'), ('test', data),
                           ('rubric', ROOT / 'docs/experiment_01_rubric.md'), ('runner', Path(__file__))]:
            if sha(path) != freeze[name + '_sha256']:
                raise ValueError(f'Frozen {name} changed')
        check_pair(load_rows(ROOT / 'data/experiment_01/dev.jsonl', 'dev'), rows)
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = {'config': cfg, 'phase': args.phase, 'status': 'starting', 'config_sha256': sha(args.config),
                'data_sha256': sha(data), 'runner_sha256': sha(__file__), 'python': platform.python_version(),
                'platform': platform.platform(), 'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                'source_dirty': bool(subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain']).strip()),
                'review': 'Synthetic cases agent-reviewed; no clinical or independent human validation'}
    def save():
        (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    save()
    try:
        import torch
        import transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
        torch.set_num_threads(cfg['threads'])
        set_seed(cfg['seed'])
        started = time.perf_counter()
        kwargs = dict(revision=cfg['model_revision'], cache_dir=str(ROOT / cfg['cache_dir']), local_files_only=True, trust_remote_code=False)
        tokenizer = AutoTokenizer.from_pretrained(cfg['model_id'], **kwargs)
        model = AutoModelForCausalLM.from_pretrained(cfg['model_id'], torch_dtype=torch.float32, **kwargs)
        model.eval()
        manifest['inherited_generation_config'] = model.generation_config.to_dict()
        manifest['effective_overrides'] = {**cfg['generation'], 'pad_token_id': tokenizer.eos_token_id}
        manifest.update(load_seconds=time.perf_counter()-started, torch=torch.__version__, transformers=transformers.__version__, device='cpu', dtype='float32', threads=torch.get_num_threads())
        save()
        rng = random.Random(cfg['seed'])
        failures = 0
        with (args.out / 'responses.jsonl').open('x', encoding='utf-8') as f:
            for row in rows:
                order = ['A', 'B']; rng.shuffle(order)
                for condition in order:
                    start = time.perf_counter()
                    record = {'scenario_id': row['scenario_id'], 'conversation_group_id': row['conversation_group_id'], 'condition': condition,
                              'input_text': row['input_text'], 'phase': args.phase, 'status': 'failed', 'response': None}
                    try:
                        set_seed(cfg['seed'])
                        messages = [{'role':'system','content':cfg['prompts'][condition]}, {'role':'user','content':row['input_text']}]
                        inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors='pt')
                        with torch.inference_mode():
                            output = model.generate(inputs, attention_mask=torch.ones_like(inputs), **cfg['generation'], pad_token_id=tokenizer.eos_token_id)
                        generated = output[0, inputs.shape[1]:]
                        response = tokenizer.decode(generated, skip_special_tokens=True)
                        if not response.strip(): raise ValueError('Empty generation')
                        record.update(status='generated', response=response, input_tokens=inputs.shape[1], output_tokens=len(generated), hit_token_limit=len(generated)==cfg['generation']['max_new_tokens'])
                    except Exception as exc:
                        record['error_type'] = type(exc).__name__; failures += 1
                    record['elapsed_seconds'] = time.perf_counter()-start
                    f.write(json.dumps(record, ensure_ascii=False)+'\n'); f.flush()
                    print(row['scenario_id'], condition, record['status'], round(record['elapsed_seconds'], 2), flush=True)
        manifest.update(status='generated_unrated' if not failures else 'completed_with_failures', failures=failures)
    except Exception as exc:
        manifest.update(status='failed', error_type=type(exc).__name__)
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
