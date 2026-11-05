"""Redacted reachable-history and build scan. Never prints credential values."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT.parent / 'relevia'
TOKEN = re.compile(rb'(?:gsk_[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})')


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def run():
    env = APP / '.env'
    values = []
    if env.exists():
        for line in env.read_bytes().splitlines():
            if b'=' in line and not line.lstrip().startswith(b'#'):
                value = line.split(b'=', 1)[1].strip().strip(b'\'"')
                if len(value) >= 20:
                    values.append(value)
    def check(data):
        return bool(TOKEN.search(data)), any(v in data for v in values)
    report = {'scope': 'all reachable Git blobs, current dist files; patterns plus exact local env value matching; no provider validation', 'repositories': {}}
    for repo in (APP, ROOT):
        objects = git(repo, 'rev-list', '--objects', '--all').decode().splitlines()
        process = subprocess.Popen(['git', '-C', str(repo), 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        matches, count, total = [], 0, 0
        try:
            for entry in objects:
                sha, _, path = entry.partition(' ')
                process.stdin.write((sha + '\n').encode()); process.stdin.flush()
                header = process.stdout.readline().decode().split()
                remaining = int(header[2]); size = remaining
                tail = b''; candidate = exact = False
                while remaining:
                    block = process.stdout.read(min(remaining, 1024 * 1024)); remaining -= len(block)
                    if header[1] == 'blob':
                        a, b = check(tail + block); candidate |= a; exact |= b
                        tail = (tail + block)[-4096:]
                process.stdout.read(1)
                if header[1] == 'blob':
                    count += 1; total += size
                    if candidate or exact:
                        matches.append({'object': sha, 'path': path, 'pattern_match': candidate, 'matches_current_env': exact})
        finally:
            process.stdin.close(); process.wait(); process.stdout.close()
        report['repositories'][repo.name] = {'blobs': count, 'bytes': total, 'matches': matches}
    files = list((APP / 'dist').rglob('*.js')) + list((APP / 'dist').rglob('*.html'))
    report['bundle'] = {'files': len(files), 'matches': [p.relative_to(APP).as_posix() for p in files if any(check(p.read_bytes()))]}
    report['env_ignored'] = subprocess.run(['git', '-C', str(APP), 'check-ignore', '-q', '.env']).returncode == 0
    report['env_tracked'] = bool(git(APP, 'ls-files', '.env').strip())
    report['provider_validity_or_rotation'] = 'not tested; no service changes authorized'
    out = ROOT / 'results/milestone_2/security.json'; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    run()
