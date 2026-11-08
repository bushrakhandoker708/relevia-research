"""Controlled LoRA pilot for condition C (same base, same prompt B, plus an adapter).

What this is for: Milestone 4 compares B (pinned Qwen2.5-1.5B-Instruct + optimised prompt)
with C (the same checkpoint + a LoRA adapter + the identical prompt). Everything except
the adapter must stay fixed, so this script reads the base revision, prompt and LoRA
settings from configs/milestone_4.pilot.json and configs/experiment_01.pilot.json rather
than taking them on the command line.

Two modes:
  --smoke   a few optimiser steps on a handful of conversations. Checks the pipeline
            (template alignment, label masking, loss going through, adapter saving,
            instrumentation). Cheap enough for a CPU. Says nothing about quality.
  --pilot   the small approved pilot (<=256 rows). Refuses to run unless
            --approved-by is given, because the milestone requires explicit approval.

Data rules (from docs/milestone_4_protocol.md): only the audited official-source
EmpatheticDialogues partitions; whole conversation groups selected with a seed; the
validation subset comes from the separate validation partition; the final test set is
never read here. Training uses prompt B as the system message so that C is trained and
evaluated under the same prompt.

Run:
  python scripts/lora_pilot.py --smoke --out results/lora/smoke-v1
  python scripts/lora_pilot.py --pilot --lr 2e-4 --approved-by "Bushra, <date>" --out results/lora/pilot-lr2e-4
"""
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

SMOKE = {'train_rows': 16, 'val_rows': 8, 'max_length': 256, 'max_steps': 4, 'grad_accum': 2}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]


def select_groups(rows, limit, seed):
    """Whole conversation groups, seeded order, stop before exceeding `limit` rows."""
    groups = {}
    for r in rows:
        groups.setdefault(r['conv_id'], []).append(r)
    order = sorted(groups)
    random.Random(seed).shuffle(order)
    chosen, total = [], 0
    for g in order:
        if total + len(groups[g]) > limit:
            continue
        chosen.append(g)
        total += len(groups[g])
        if total == limit:
            break
    return [r for g in chosen for r in groups[g]], chosen


def build_example(tok, system, row, max_length):
    """Token ids with labels only on the final assistant reply; None if it is cut off entirely."""
    msgs = [{'role': 'system', 'content': system}, *row['history'], {'role': 'user', 'content': row['prompt']}]
    prompt_ids = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True)
    full_ids = tok.apply_chat_template(msgs + [{'role': 'assistant', 'content': row['response']}], tokenize=True)
    prompt_ids = list(prompt_ids['input_ids'] if hasattr(prompt_ids, 'keys') else prompt_ids)
    full_ids = list(full_ids['input_ids'] if hasattr(full_ids, 'keys') else full_ids)
    if full_ids[:len(prompt_ids)] != prompt_ids:
        raise ValueError('Chat template prefix mismatch: label masking would be misaligned')
    truncated = len(full_ids) > max_length
    full_ids = full_ids[:max_length]
    labels = [-100] * min(len(prompt_ids), len(full_ids)) + full_ids[len(prompt_ids):]
    if all(x == -100 for x in labels):
        return None, truncated
    return {'input_ids': full_ids, 'labels': labels}, truncated


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--smoke', action='store_true')
    mode.add_argument('--pilot', action='store_true')
    ap.add_argument('--lr', type=float, default=2e-4)
    ap.add_argument('--approved-by', default=None, help='required for --pilot: who approved it and when')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    m4 = json.loads((ROOT / 'configs/milestone_4.pilot.json').read_text(encoding='utf-8'))
    exp = json.loads((ROOT / 'configs/experiment_01.pilot.json').read_text(encoding='utf-8'))
    if args.pilot and not args.approved_by:
        raise SystemExit('The pilot needs explicit approval: pass --approved-by "<name>, <date>".')
    if args.lr not in m4['proposed_training']['learning_rate_candidates']:
        raise SystemExit(f"--lr must be one of the pre-registered candidates {m4['proposed_training']['learning_rate_candidates']}")
    if m4['model_revision'] != exp['model_revision']:
        raise SystemExit('Milestone 4 base revision differs from the prompting baseline; B vs C would not be controlled.')
    data = m4['data']
    for key in ('training_partition', 'validation_partition'):
        if 'quarantine' in data[key]:
            raise SystemExit('Quarantined data is not allowed')
    if sha(ROOT / data['training_partition']) != data['training_sha256']:
        raise SystemExit('Training partition changed since it was frozen')

    tp = m4['proposed_training']
    settings = dict(SMOKE) if args.smoke else {'train_rows': 256, 'val_rows': 64, 'max_length': tp['max_length'],
                                                'max_steps': None, 'grad_accum': tp['gradient_accumulation_steps']}
    seed = tp['seed']
    train_rows, train_groups = select_groups(read_jsonl(ROOT / data['training_partition']), settings['train_rows'], seed)
    val_rows, val_groups = select_groups(read_jsonl(ROOT / data['validation_partition']), settings['val_rows'], seed + 1)
    if set(train_groups) & set(val_groups):
        raise SystemExit('Training and validation groups overlap')

    args.out.mkdir(parents=True, exist_ok=False)
    adapter_dir = ROOT / 'adapters' / args.out.name  # adapters/ is gitignored
    manifest = {
        'status': 'starting', 'mode': 'smoke' if args.smoke else 'pilot', 'approved_by': args.approved_by,
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'model_id': m4['model_id'], 'model_revision': m4['model_revision'], 'prompt': 'experiment_01.pilot.json:prompts.B',
        'prompt_sha256': hashlib.sha256(exp['prompts']['B'].encode()).hexdigest(),
        'lora': m4['lora'], 'learning_rate': args.lr, 'seed': seed, 'settings': settings,
        'train_sha256': data['training_sha256'], 'train_rows': len(train_rows), 'train_groups': len(train_groups),
        'train_ids_sha256': hashlib.sha256('\n'.join(r['id'] for r in train_rows).encode()).hexdigest(),
        'val_rows': len(val_rows), 'val_groups': len(val_groups),
        'val_ids_sha256': hashlib.sha256('\n'.join(r['id'] for r in val_rows).encode()).hexdigest(),
        'final_test_read': False, 'python': platform.python_version(), 'platform': platform.platform(),
        'runner_sha256': sha(__file__), 'adapter_dir': str(adapter_dir.relative_to(ROOT)),
    }
    save = lambda: (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    save()
    (args.out / 'selection.json').write_text(json.dumps({'train_ids': [r['id'] for r in train_rows],
                                                          'val_ids': [r['id'] for r in val_rows]}, indent=1), encoding='utf-8')
    losses = (args.out / 'losses.jsonl').open('x', encoding='utf-8')
    try:
        import psutil
        import torch
        import transformers
        import peft
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import LoraConfig, get_peft_model
        torch.manual_seed(seed)
        random.seed(seed)
        proc = psutil.Process()
        cuda = torch.cuda.is_available()
        dtype = (torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16) if cuda else torch.float32
        manifest.update(torch=torch.__version__, transformers=transformers.__version__, peft=peft.__version__,
                        device='cuda:' + torch.cuda.get_device_name(0) if cuda else 'cpu', dtype=str(dtype),
                        threads=torch.get_num_threads())
        t0 = time.perf_counter()
        kw = dict(revision=m4['model_revision'], cache_dir=str(ROOT / exp['cache_dir']), local_files_only=True)
        tok = AutoTokenizer.from_pretrained(m4['model_id'], **kw)
        model = AutoModelForCausalLM.from_pretrained(m4['model_id'], dtype=dtype, **kw)
        if cuda:
            model.to('cuda')
        model.config.use_cache = False
        model.gradient_checkpointing_enable()
        model.enable_input_require_grads()
        lcfg = m4['lora']
        model = get_peft_model(model, LoraConfig(r=lcfg['rank'], lora_alpha=lcfg['alpha'], lora_dropout=lcfg['dropout'],
                                                 target_modules=lcfg['target_modules'], bias=lcfg['bias'], task_type='CAUSAL_LM'))
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        manifest.update(setup_seconds=time.perf_counter() - t0, trainable_parameters=trainable,
                        total_parameters=sum(p.numel() for p in model.parameters()), rss_after_load_bytes=proc.memory_info().rss)
        save()

        def encode(rows):
            out, cut, dropped = [], 0, 0
            for r in rows:
                ex, was_cut = build_example(tok, exp['prompts']['B'], r, settings['max_length'])
                cut += was_cut
                if ex is None:
                    dropped += 1
                else:
                    out.append(ex)
            return out, cut, dropped
        train, t_cut, t_drop = encode(train_rows)
        val, v_cut, v_drop = encode(val_rows)
        manifest.update(train_examples=len(train), train_truncated=t_cut, train_dropped_fully_truncated=t_drop,
                        val_examples=len(val), val_truncated=v_cut, val_dropped_fully_truncated=v_drop,
                        train_target_tokens=sum(sum(x != -100 for x in e['labels']) for e in train))
        device = next(model.parameters()).device

        def batch(e):
            return (torch.tensor([e['input_ids']], device=device), torch.tensor([e['labels']], device=device))

        def val_loss():
            model.eval()
            total, tokens = 0.0, 0
            with torch.no_grad():
                for e in val:
                    ids, labels = batch(e)
                    n = sum(x != -100 for x in e['labels']) - 1  # shifted targets
                    total += model(input_ids=ids, labels=labels).loss.item() * max(n, 1)
                    tokens += max(n, 1)
            model.train()
            return total / tokens if tokens else None

        opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr,
                                weight_decay=tp['weight_decay'])
        manifest['val_loss_before'] = val_loss()
        save()
        model.train()
        order = list(range(len(train)))
        random.Random(seed).shuffle(order)
        steps_per_epoch = len(order) // settings['grad_accum']
        max_steps = settings['max_steps'] or steps_per_epoch * tp['epochs']
        if cuda:
            torch.cuda.reset_peak_memory_stats()
        t_train, step, micro = time.perf_counter(), 0, 0
        while step < max_steps:
            for i in order:
                ids, labels = batch(train[i])
                loss = model(input_ids=ids, labels=labels).loss
                if not torch.isfinite(loss):
                    raise FloatingPointError('Non-finite training loss')
                (loss / settings['grad_accum']).backward()
                micro += 1
                losses.write(json.dumps({'micro_step': micro, 'loss': loss.item(), 'tokens': ids.shape[1]}) + '\n')
                if micro % settings['grad_accum'] == 0:
                    opt.step()
                    opt.zero_grad()
                    step += 1
                    losses.write(json.dumps({'optimizer_step': step, 'elapsed_seconds': time.perf_counter() - t_train}) + '\n')
                    losses.flush()
                    print(f'step {step}/{max_steps} loss {loss.item():.3f}', flush=True)
                    if step >= max_steps:
                        break
        manifest.update(training_seconds=time.perf_counter() - t_train, optimizer_steps=step, micro_steps=micro,
                        val_loss_after=val_loss(), rss_after_training_bytes=proc.memory_info().rss,
                        peak_allocated_device_bytes=torch.cuda.max_memory_allocated() if cuda else None)
        model.save_pretrained(adapter_dir)
        manifest['adapter_bytes'] = sum(f.stat().st_size for f in adapter_dir.rglob('*') if f.is_file())
        manifest['status'] = 'completed'
    except BaseException as exc:
        manifest.update(status='interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed',
                        error=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        losses.close()
        manifest['ended_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    print(json.dumps({k: manifest[k] for k in ('status', 'trainable_parameters', 'val_loss_before', 'val_loss_after',
                                                'training_seconds', 'adapter_bytes')}, indent=2))


if __name__ == '__main__':
    main()
