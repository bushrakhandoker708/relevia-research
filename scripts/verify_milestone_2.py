"""Run local Milestone 2 checks and retain exit codes, not invented metrics."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT.parent / 'relevia'
npm = 'npm.cmd' if os.name == 'nt' else 'npm'
lint_files = ['src/services/db.js', 'src/services/chatStorage.js', 'src/services/releviaBrain.js',
              'src/services/personalLetter.js', 'src/services/groqApi.js', 'src/components/Chatbot.jsx',
              'src/components/ChatPrivacy.jsx', 'src/components/ErrorBoundary.jsx',
              'src/components/errorBoundaryHelpers.jsx', 'tests/inference.test.js', 'tests/storage.test.js', 'eslint.config.js']
checks = [
    ('javascript_tests', APP, [npm, 'test']),
    ('changed_lint', APP, ['node', 'node_modules/eslint/bin/eslint.js', *lint_files, '--max-warnings', '0']),
    ('production_build', APP, [npm, 'run', 'build']),
    ('legacy_full_lint', APP, [npm, 'run', 'lint']),
    ('python_tests', ROOT, [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
    ('dataset_rebuild', ROOT, [sys.executable, 'data/build_dataset.py']),
    ('leakage', ROOT, [sys.executable, 'scripts/check_leakage.py']),
    ('security', ROOT, [sys.executable, 'scripts/security_audit.py']),
]
report = {'date': '2026-11-05', 'scope': 'local automated checks; browser UI validation not completed', 'checks': {}}
for name, cwd, command in checks:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    output = result.stdout + result.stderr
    report['checks'][name] = {'command': command, 'exit_code': result.returncode, 'output_tail': output.splitlines()[-18:]}
    print(f'{name}: exit {result.returncode}', flush=True)
out = ROOT / 'results/milestone_2/verification.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
sys.exit(any(value['exit_code'] != 0 for name, value in report['checks'].items() if name != 'legacy_full_lint'))
