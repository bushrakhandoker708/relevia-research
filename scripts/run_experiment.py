"""Local, revision-pinned benchmark harness. --prepare never loads a model."""
import argparse
import hashlib
import json
import platform
import random
import re
import subprocess
import time
from pathlib import Path

QUALITY = ['emotional_acknowledgment', 'contextual_relevance', 'specificity', 'helpfulness', 'clarity', 'autonomy']
SAFETY = ['unsupported_medical_claim', 'false_reassurance', 'harmful_agreement', 'inappropriate_refusal', 'dependency_language', 'unsafe_escalation']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(config, rows):
    for field in ['experiment_id', 'condition', 'model_id', 'model_revision', 'prompt_version', 'prompt', 'dataset_version', 'seed', 'generation']:
        if field not in config or config[field] is None:
            raise ValueError(f'Missing {field}')
    if not re.fullmatch(r'[0-9a-f]{40}', config['model_revision']):
        raise ValueError('model_revision must be an immutable 40-character commit SHA')
    for field in ['experiment_id', 'model_id', 'prompt_version', 'dataset_version']:
        if not isinstance(config[field], str) or not config[field].strip():
            raise ValueError(f'{field} must be a nonempty string')
    if config['condition'] not in ['A', 'B']:
        raise ValueError('Milestone 2 harness supports base-model A/B only; adaptation is deferred')
    if not isinstance(config['seed'], int):
        raise ValueError('seed must be an integer')
    if not isinstance(config['prompt'], str) or not config['prompt'].strip():
        raise ValueError('prompt must be nonempty')
    generation = config['generation']
    if set(generation) != {'max_new_tokens', 'do_sample'}:
        raise ValueError('Unexpected generation settings for the initial greedy pilot')
    if not isinstance(generation.get('max_new_tokens'), int) or generation['max_new_tokens'] <= 0:
        raise ValueError('max_new_tokens must be positive')
    if generation.get('do_sample') is not False:
        raise ValueError('Primary pilot uses greedy decoding: do_sample must be false')
    if not rows or len({r['scenario_id'] for r in rows}) != len(rows):
        raise ValueError('Dataset must be nonempty with unique scenario IDs')
    for row in rows:
        if row.get('source') != 'synthetic' or row.get('split') != 'dev' or row.get('source_license') != 'CC0-1.0':
            raise ValueError('Initial harness accepts only the declared synthetic CC0 development fixtures')
        if not isinstance(row.get('input_text'), str) or not row['input_text'].strip():
            raise ValueError('input_text required')


def execute(config, rows, generate):
    """Inject a local generator; tests use a stub, never report it as model evidence."""
    validate(config, rows)
    random.seed(config['seed'])
    for row in rows:
        start = time.perf_counter()
        response = None
        try:
            response = generate(config['prompt'], row['input_text'], config['generation'])
            if not isinstance(response, str) or not response.strip():
                raise ValueError('Empty/non-string generation')
            status, error = 'generated', None
        except Exception as exc:
            status, error = 'failed', type(exc).__name__
            response = None
        yield {'experiment_id': config['experiment_id'], 'condition': config['condition'],
               'scenario_id': row['scenario_id'], 'conversation_group_id': row['conversation_group_id'],
               'input_text': row['input_text'], 'response': response, 'status': status,
               'error_type': error, 'elapsed_seconds': time.perf_counter() - start,
               'quality': dict.fromkeys(QUALITY), 'safety': dict.fromkeys(SAFETY), 'annotation_status': 'unrated'}


def local_generator(config):
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    set_seed(config['seed'])
    args = dict(revision=config['model_revision'], local_files_only=True, trust_remote_code=False)
    tok = AutoTokenizer.from_pretrained(config['model_id'], **args)
    model = AutoModelForCausalLM.from_pretrained(config['model_id'], **args)
    model.eval()
    def generate(prompt, user, params):
        ids = tok.apply_chat_template([{'role': 'system', 'content': prompt}, {'role': 'user', 'content': user}],
                                      add_generation_prompt=True, return_tensors='pt')
        with torch.inference_mode():
            output = model.generate(ids, **params)
        return tok.decode(output[0, ids.shape[1]:], skip_special_tokens=True)
    return generate, {'torch': torch.__version__, 'transformers': transformers.__version__, 'device': 'cpu',
                      'threads': torch.get_num_threads(), 'processor': platform.processor()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=Path, required=True)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--prepare', action='store_true')
    args = ap.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    rows = [json.loads(line) for line in args.data.read_text(encoding='utf-8').splitlines() if line.strip()]
    validate(config, rows)
    args.out.mkdir(parents=True, exist_ok=False)  # never overwrite a previous experiment
    try:
        revision = subprocess.check_output(['git', '-C', str(Path(__file__).resolve().parents[1]), 'rev-parse', 'HEAD']).decode().strip()
    except subprocess.CalledProcessError:
        revision = None
    manifest = {**config, 'source_commit': revision, 'harness_sha256': digest(__file__),
                'source_dirty': bool(subprocess.check_output(['git', '-C', str(Path(__file__).resolve().parents[1]), 'status', '--porcelain']).strip()),
                'config_sha256': digest(args.config), 'dataset_sha256': digest(args.data),
                'prompt_sha256': hashlib.sha256(config['prompt'].encode()).hexdigest(),
                'python': platform.python_version(), 'platform': platform.platform(),
                'status': 'prepared_not_run' if args.prepare else 'starting',
                'nondeterminism': 'Seeds do not guarantee identical results across runtimes/hardware.'}
    def save():
        (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    save()
    if args.prepare:
        print('Prepared only; no responses or scores generated.'); return
    try:
        generate, environment = local_generator(config)
        manifest['runtime'] = environment
        failures = 0
        with (args.out / 'responses.jsonl').open('x', encoding='utf-8') as stream:
            for result in execute(config, rows, generate):
                failures += result['status'] == 'failed'
                stream.write(json.dumps(result, ensure_ascii=False) + '\n'); stream.flush()
        manifest.update(status='completed_with_failures' if failures else 'generated_unrated', failures=failures)
    except Exception as exc:
        manifest.update(status='failed', error_type=type(exc).__name__)
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
