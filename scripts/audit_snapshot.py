"""Read-only source/data audit. Does not print conversations or credential values."""
import ast
import hashlib
import itertools
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT.parent / 'relevia'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.DEVNULL)


def main():
    report = {'scope': 'local snapshot; no generation, training, or clinical evaluation'}
    report['commits'] = {p.name: git(p, 'rev-parse', 'HEAD').decode().strip() for p in (APP, ROOT)}
    files = [*APP.glob('src/services/*.js'), APP / 'src/components/Chatbot.jsx',
             APP / 'package.json', APP / 'package-lock.json', APP / 'README.md']
    report['sha256'] = {p.relative_to(ROOT.parent).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    splits = {p.stem: [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
              for p in (ROOT / 'data/processed').glob('*.jsonl')}
    report['splits'] = {k: {'rows': len(v), 'conversations': len({r['conv_id'] for r in v}),
                          'sha256': hashlib.sha256((ROOT / 'data/processed' / (k + '.jsonl')).read_bytes()).hexdigest()}
                        for k, v in splits.items()}
    report['conversation_overlap'] = {a + '__' + b: len({r['conv_id'] for r in splits[a]} & {r['conv_id'] for r in splits[b]})
                                      for a, b in itertools.combinations(sorted(splits), 2)}
    report['safety_fixture_counts'] = {p.name: sum(bool(s.strip()) for s in p.read_text(encoding='utf-8').splitlines())
                                       for p in (ROOT / 'data/safety').glob('*.jsonl')}
    report['python_syntax'] = {}
    for p in [*ROOT.glob('src/*.py'), ROOT / 'data/build_dataset.py', ROOT / 'deploy/export_to_webllm.py']:
        try:
            ast.parse(p.read_text(encoding='utf-8-sig'))
            report['python_syntax'][p.relative_to(ROOT).as_posix()] = 'pass'
        except SyntaxError as e:
            report['python_syntax'][p.relative_to(ROOT).as_posix()] = str(e)
    report['notebooks'] = {p.name: {'cells': len((n := json.loads(p.read_text(encoding='utf-8')))['cells']),
                                      'executed_cells': sum(c.get('execution_count') is not None for c in n['cells'])}
                           for p in (ROOT / 'notebooks').glob('*.ipynb')}
    # Narrow token-pattern screen over all reachable history; not a comprehensive secret scanner.
    pattern = re.compile(rb'(?:gsk_[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})')
    matches = []
    for repo in (APP, ROOT):
        objects = git(repo, 'rev-list', '--objects', '--all').decode().splitlines()
        blobs = 0
        for obj in objects:
            sha, _, name = obj.partition(' ')
            if git(repo, 'cat-file', '-t', sha).strip() != b'blob':
                continue
            if int(git(repo, 'cat-file', '-s', sha)) > 2_000_000:
                continue
            blobs += 1
            if pattern.search(git(repo, 'cat-file', 'blob', sha)):
                matches.append({'repository': repo.name, 'object': sha, 'path': name})
        report.setdefault('history_screen', {})[repo.name] = {'blobs_under_2MB_scanned': blobs}
    report['history_screen']['candidate_locations_no_values'] = matches
    report['local_env_token_pattern_present'] = bool(pattern.search((APP / '.env').read_bytes())) if (APP / '.env').exists() else None
    lock = json.loads((APP / 'package-lock.json').read_text())
    report['locked_webllm'] = lock['packages']['node_modules/@mlc-ai/web-llm']['version']
    out = ROOT / 'results/audit/snapshot.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
