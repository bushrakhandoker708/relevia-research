// Compare S0, S1, S2 and S3 on routing only. Response quality is not measured here.
//
// Evidence roles:
//   heldout_v4   77 cases frozen (data/safety_v4/freeze.json) before any S3 code was
//                written. PRIMARY S3 result. The same agent wrote the cases and S3, so it
//                is not independent. The first run is recorded with S3's hash; any later
//                rule change must be reported as post hoc, never silently re-run.
//   heldout_v3, v2_all   development evidence for S3 (S3 was tuned on them).
//
// Run:  node scripts/evaluate_safety_s3.mjs           (writes results/safety/s3-v1/)
//       node scripts/evaluate_safety_s3.mjs --verify
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import * as S1 from '../detectors/s1/safety.js';
import * as S2 from '../detectors/s2/safety.js';
import * as S3 from '../../relevia/src/services/safetyS3.js';

const root = new URL('../', import.meta.url);
const sha = url => createHash('sha256').update(readFileSync(url)).digest('hex');
const v4 = JSON.parse(readFileSync(new URL('data/safety_v4/freeze.json', root)));
if (sha(new URL('data/safety_v4/heldout.jsonl', root)) !== v4.sha256) throw Error('v4 held-out set changed');
const s2rec = JSON.parse(readFileSync(new URL('results/safety/s2-v1/evaluation.json', root))).s2_sha256;
if (sha(new URL('detectors/s2/safety.js', root)) !== s2rec) throw Error('S2 copy differs from the recorded S2');
if (S3.DETECTOR_VERSION !== 'S3') throw Error('Application detector is not S3');

const read = p => readFileSync(new URL(p, root), 'utf8').trim().split('\n').map(l => JSON.parse(l));
const detectors = {
  S0: t => (S1.CRISIS_RE.test(t) ? 'urgent' : 'none'),
  S1: (t, h) => S1.assessRisk(t, h).level,
  S2: (t, h) => S2.assessRisk(t, h).level,
  S3: (t, h) => S3.assessRisk(t, h).level,
};
const TIERS = ['emergency', 'urgent', 'check_in', 'none'];

function wilson(k, n) {
  if (!n) return null;
  const z = 1.959963984540054, p = k / n, den = 1 + z * z / n;
  const c = (p + z * z / (2 * n)) / den, r = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den;
  return [Math.max(0, c - r), Math.min(1, c + r)];
}
function exactMcNemar(b, c) {
  const n = b + c;
  if (!n) return 1;
  let p = 0;
  for (let k = 0; k <= Math.min(b, c); k++) { let x = 1; for (let i = 0; i < k; i++) x = x * (n - i) / (i + 1); p += x; }
  return Math.min(1, 2 * p / 2 ** n);
}

function score(cases) {
  const out = { n: cases.length, ambiguous: cases.filter(c => c.expected_urgent === null).length, detectors: {} };
  const labelled = cases.filter(c => c.expected_urgent !== null);
  for (const [name, f] of Object.entries(detectors)) {
    const m = { tp: 0, fn: 0, fp: 0, tn: 0, check_in_on_urgent: 0, check_in_on_non_urgent: 0, missed: [], false_alarms: [] };
    for (const c of labelled) {
      const level = f(c.text, c.history || []);
      if (c.expected_urgent) { level === 'urgent' ? m.tp++ : (m.fn++, m.missed.push(c.id)); if (level === 'check_in') m.check_in_on_urgent++; }
      else { level === 'urgent' ? (m.fp++, m.false_alarms.push(c.id)) : m.tn++; if (level === 'check_in') m.check_in_on_non_urgent++; }
    }
    m.recall = m.tp / (m.tp + m.fn); m.recall_wilson95 = wilson(m.tp, m.tp + m.fn);
    m.false_positive_rate = m.fp / (m.fp + m.tn); m.fpr_wilson95 = wilson(m.fp, m.fp + m.tn);
    m.ambiguous_routed = { check_in: 0, urgent: 0, none: 0 };
    for (const c of cases.filter(x => x.expected_urgent === null)) m.ambiguous_routed[f(c.text, c.history || [])]++;
    out.detectors[name] = m;
  }
  return out;
}

const rows4 = read('data/safety_v4/heldout.jsonl');
const result = {
  scope: 'Routing only; agent-authored synthetic labels; not clinical validation',
  s3_sha256: sha(new URL('../../relevia/src/services/safetyS3.js', import.meta.url)),
  s2_sha256: s2rec,
  heldout_v4: score(rows4),
  heldout_v3: score(read('data/safety_v3/heldout.jsonl')),
  v2_all: score([...read('data/safety_v2/development.jsonl'), ...read('data/safety_v2/heldout.jsonl')]),
};
// S3 tier confusion on v4: expected tier (rows) x predicted tier (columns)
const conf = {};
for (const e of ['emergency', 'urgent', 'ambiguous', 'none']) conf[e] = Object.fromEntries(TIERS.map(t => [t, 0]));
const perCase = rows4.map(c => {
  const r = S3.assessRisk(c.text, c.history || []);
  conf[c.expected_tier][r.tier]++;
  return { id: c.id, category: c.category, text: c.text, expected: c.expected_tier,
    s2: S2.assessRisk(c.text, c.history || []).level, s3: r.tier, reason: r.reason };
});
const v = result.heldout_v4;
v.s3_tier_confusion = conf;
const nEm = rows4.filter(c => c.expected_tier === 'emergency').length;
v.s3_emergency_recall = { k: conf.emergency.emergency, n: nEm, wilson95: wilson(conf.emergency.emergency, nEm) };
v.s3_emergency_on_non_emergency = perCase.filter(c => c.s3 === 'emergency' && c.expected !== 'emergency').map(c => c.id);
const urgentCases = perCase.filter(c => ['emergency', 'urgent'].includes(c.expected));
const s3hit = c => ['urgent', 'emergency'].includes(c.s3);
const s2only = urgentCases.filter(c => c.s2 === 'urgent' && !s3hit(c)).length;
const s3only = urgentCases.filter(c => c.s2 !== 'urgent' && s3hit(c)).length;
v.mcnemar_s2_vs_s3_on_urgent = { s2_only: s2only, s3_only: s3only, exact_p: exactMcNemar(s2only, s3only) };
v.by_category = Object.fromEntries([...new Set(rows4.map(r => r.category))].map(cat => {
  const rs = rows4.filter(r => r.category === cat && r.expected_urgent !== null);
  return [cat, Object.fromEntries(Object.keys(detectors).map(d => [d,
    rs.filter(r => (detectors[d](r.text, r.history) === 'urgent') === r.expected_urgent).length + '/' + rs.length]))];
}));
v.cases = perCase;

// --posthoc: S3 changed after its first v4 run. Those numbers are written separately and
// are NOT held-out evidence, because the fixes were made after seeing the v4 misses.
// --posthoc[=name]: written to results/safety/s3-v1-<name>/ (default "posthoc").
const phArg = process.argv.find(a => a.startsWith('--posthoc'));
const posthoc = Boolean(phArg);
if (posthoc) result.posthoc = 'Rules changed after the first v4 run (s3-v1). v4 is development evidence for this version.';
const dir = new URL(posthoc ? `results/safety/s3-v1-${phArg.split('=')[1] || 'posthoc'}/` : 'results/safety/s3-v1/', root);
const text = JSON.stringify(result, null, 2) + '\n';
if (process.argv.includes('--verify')) {
  const rec = JSON.parse(readFileSync(new URL('evaluation.json', dir), 'utf8'));
  if (rec.s3_sha256 !== result.s3_sha256) {
    // A record made with an earlier S3 is kept as history; it cannot be re-derived from today's S3.
    if (!rec.s3_sha256) throw Error('record has no S3 hash');
    console.log(`Historical record for S3 ${rec.s3_sha256.slice(0, 12)} (current ${result.s3_sha256.slice(0, 12)}); not re-derivable`);
    process.exit(0);
  }
  if (readFileSync(new URL('evaluation.json', dir), 'utf8') !== text) throw Error('S3 evidence does not reproduce');
  console.log('Verified S3 evidence without changing it');
} else {
  if (existsSync(new URL('evaluation.json', dir))) throw Error(`${dir.pathname} exists; recorded runs are never overwritten`);
  mkdirSync(dir, { recursive: true });
  writeFileSync(new URL('evaluation.json', dir), text);
  console.log('Wrote ' + dir.pathname.split('/results/')[1] + 'evaluation.json');
}
