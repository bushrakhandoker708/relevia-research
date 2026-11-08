"""Offline fixed-model evaluation with streaming timestamps, never training."""
import argparse
import hashlib
import json
import os
import platform
import random
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
ROOT = Path(__file__).resolve().parents[1]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['expanded', 'performance'], required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    freeze = json.loads((ROOT / 'configs/expanded.freeze.json').read_text())
    for name, expected in freeze['sha256'].items():
        if digest(ROOT / name) != expected:
            raise ValueError('Frozen artifact changed: ' + name)
    cfg = json.loads((ROOT / 'configs/experiment_01.pilot.json').read_text())
    data = ROOT / ('data/experiment_01_expanded/test.jsonl' if args.mode == 'expanded' else 'data/experiment_01/test.jsonl')
    rows = [json.loads(s) for s in data.read_text(encoding='utf-8').splitlines()]
    if args.mode == 'performance':
        rows = [dict(next(r for r in rows if r['scenario_id'] == 'test-03'), repeat=i) for i in range(1, 6)]
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = {'status': 'starting', 'mode': args.mode, 'config': cfg, 'data_sha256': digest(data),
                'runner_sha256': digest(Path(__file__)), 'python': platform.python_version(),
                'platform': platform.platform(), 'started_utc': datetime.now(timezone.utc).isoformat(),
                'max_context_tokens': 2048, 'quality_ratings': None, 'device': 'cpu', 'dtype': 'float32',
                'memory_measurement': 'Process RSS at boundaries, not peak or model-only memory',
                'prefill_note': 'TTFT includes prefill and first-token framework overhead; pure prefill throughput not measured',
                'cold_start_note': 'Fresh process; OS file cache not cleared. No browser measurements.'}
    def save():
        (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    save()
    failures = 0
    try:
        import torch
        import transformers
        import psutil
        from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
        from transformers.generation.streamers import BaseStreamer
        torch.set_num_threads(cfg['threads'])
        set_seed(cfg['seed'])
        process = psutil.Process()
        class ClockStream(BaseStreamer):
            def __init__(self):
                self.prompt = True
                self.times = []
            def put(self, value):
                if self.prompt:
                    self.prompt = False
                else:
                    self.times.append(time.perf_counter())
            def end(self):
                pass
        start = time.perf_counter()
        kwargs = dict(revision=cfg['model_revision'], cache_dir=str(ROOT/cfg['cache_dir']), local_files_only=True, trust_remote_code=False)
        tokenizer = AutoTokenizer.from_pretrained(cfg['model_id'], **kwargs)
        manifest['tokenizer_load_seconds'] = time.perf_counter()-start
        start = time.perf_counter()
        model = AutoModelForCausalLM.from_pretrained(cfg['model_id'], torch_dtype=torch.float32, **kwargs)
        model.eval()
        manifest.update(model_load_seconds=time.perf_counter()-start, rss_loaded_bytes=process.memory_info().rss,
                        torch=torch.__version__, transformers=transformers.__version__, threads=torch.get_num_threads(),
                        inherited_generation_config=model.generation_config.to_dict())
        save()
        rng = random.Random(42)
        # Recorded warm-up is excluded from paired test results, never silently discarded.
        warmup = {'scenario_id': 'warmup', 'input_text': 'Please say hello briefly.', 'conversation_group_id': 'warmup'}
        schedule = [(warmup, 'A', True)]
        for row in rows:
            order = ['A', 'B']; rng.shuffle(order)
            schedule.extend((row, c, False) for c in order)
        with (args.out/'responses.jsonl').open('x', encoding='utf-8') as f:
            for row, condition, is_warmup in schedule:
                record = {**row, 'condition': condition, 'warmup': is_warmup, 'status': 'failed', 'started_utc': datetime.now(timezone.utc).isoformat()}
                started = time.perf_counter(); cpu = time.process_time()
                record['rss_before_bytes'] = process.memory_info().rss
                try:
                    set_seed(cfg['seed'])
                    inputs = tokenizer.apply_chat_template([{'role':'system','content':cfg['prompts'][condition]}, {'role':'user','content':row['input_text']}], add_generation_prompt=True, return_tensors='pt')
                    if inputs.shape[1] + cfg['generation']['max_new_tokens'] > 2048:
                        raise ValueError('Context budget exceeded; refusing silent truncation')
                    stream = ClockStream(); generation_start = time.perf_counter()
                    with torch.inference_mode():
                        output = model.generate(inputs, attention_mask=torch.ones_like(inputs), streamer=stream, **cfg['generation'], pad_token_id=tokenizer.eos_token_id)
                    generated = output[0, inputs.shape[1]:]
                    text = tokenizer.decode(generated, skip_special_tokens=True)
                    if not text.strip(): raise ValueError('Empty response')
                    record.update(status='generated', response=text, input_tokens=int(inputs.shape[1]), output_tokens=len(generated),
                                  hit_token_limit=len(generated)==cfg['generation']['max_new_tokens'],
                                  tokenisation_seconds=generation_start-started,
                                  ttft_seconds=stream.times[0]-generation_start if stream.times else None,
                                  decode_tokens_per_second=(len(stream.times)-1)/(stream.times[-1]-stream.times[0]) if len(stream.times)>1 else None)
                except Exception as exc:
                    record['error_type'] = type(exc).__name__; failures += 1
                record.update(elapsed_seconds=time.perf_counter()-started, process_cpu_seconds=time.process_time()-cpu,
                              rss_after_bytes=process.memory_info().rss, ended_utc=datetime.now(timezone.utc).isoformat())
                f.write(json.dumps(record, ensure_ascii=False)+'\n'); f.flush()
                print(row['scenario_id'], row.get('repeat',''), condition, record['status'], round(record['elapsed_seconds'],2), flush=True)
        manifest.update(status='generated_unrated' if not failures else 'completed_with_failures', failures=failures)
    except BaseException as exc:
        manifest.update(status='interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed', error_type=type(exc).__name__)
        raise
    finally:
        manifest['ended_utc'] = datetime.now(timezone.utc).isoformat(); save()


if __name__ == '__main__':
    main()
