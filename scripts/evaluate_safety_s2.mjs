// Compare S0 (original regex), S1 (frozen copy) and S2 (the application's current
// safety.js) on routing only. Response quality is not measured here.
//
// Evidence roles:
//   development: safety_v2 development + held-out cases and their eleven perturbations.
//                S2 was designed against these failure types, so S2 scores here are
//                optimistic by construction.
//   heldout_v3:  45 new cases frozen (data/safety_v3/freeze.json) before any S2 rule
//                was written. This is the primary S2 result. The same agent wrote both
//                the cases and S2, so it is not an independent test.
//
// Run:  node scripts/evaluate_safety_s2.mjs        (writes results/safety/s2-v1/)
//       node scripts/evaluate_safety_s2.mjs --verify
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import * as S1 from '../detectors/s1/safety.js';
import * as S2 from '../../relevia/src/services/safety.js';
import { PERTURBATIONS } from './perturbations.mjs';

const root = new URL('../', import.meta.url);
const sha = url => createHash('sha256').update(readFileSync(url)).digest('hex');
const v2 = JSON.parse(readFileSync(new URL('data/safety_v2/freeze.json', root)));
const v3 = JSON.parse(readFileSync(new URL('data/safety_v3/freeze.json', root)));
for (const n of ['development.jsonl', 'heldout.jsonl']) if (sha(new URL('data/safety_v2/' + n, root)) !== v2[n]) throw Error('v2 suite changed');
if (sha(new URL('data/safety_v3/heldout.jsonl', root)) !== v3['heldout.jsonl']) throw Error('v3 held-out set changed');
if (sha(new URL('../detectors/s1/safety.js', import.meta.url)) !== v2.detector_sha256) throw Error('S1 copy changed');
if (S2.DETECTOR_VERSION !== 'S2') throw Error('Application detector is not S2');

const read = path => readFileSync(new URL(path, root), 'utf8').trim().split('\n').map(l => JSON.parse(l));
const detectors = {
  S0: text => (S1.CRISIS_RE.test(text) ? 'urgent' : 'none'),
  S1: (text, h) => S1.assessRisk(text, h).level,
  S2: (text, h) => S2.assessRisk(text, h).level,
};

function wilson(k, n) {
  if (!n) return null;
  const z = 1.959963984540054, p = k / n, den = 1 + z * z / n;
  const c = (p + z * z / (2 * n)) / den, r = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den;
  return [Math.max(0, c - r), Math.min(1, c + r)];
}

function score(cases) {
  const out = { n: cases.length, ambiguous_excluded: cases.filter(c => c.expected_urgent === null).length, detectors: {} };
  const labelled = cases.filter(c => c.expected_urgent !== null);
  for (const [name, f] of Object.entries(detectors)) {
    const m = { tp: 0, fn: 0, fp: 0, tn: 0, check_in_on_urgent: 0, check_in_on_non_urgent: 0, missed: [], false_alarms: [] };
    for (const c of labelled) {
      const level = f(c.text, c.history || []);
      const urgent = level === 'urgent';
      if (c.expected_urgent) { urgent ? m.tp++ : (m.fn++, m.missed.push(c.id)); if (level === 'check_in') m.check_in_on_urgent++; }
      else { urgent ? (m.fp++, m.false_alarms.push(c.id)) : m.tn++; if (level === 'check_in') m.check_in_on_non_urgent++; }
    }
    m.recall = m.tp / (m.tp + m.fn); m.recall_wilson95 = wilson(m.tp, m.tp + m.fn);
    m.false_positive_rate = m.fp / (m.fp + m.tn); m.fpr_wilson95 = wilson(m.fp, m.fp + m.tn);
    out.detectors[name] = m;
  }
  return out;
}

const base = [...read('data/safety_v2/development.jsonl'), ...read('data/safety_v2/heldout.jsonl')];
const result = {
  scope: 'Routing only; agent-authored synthetic labels; not clinical validation',
  s2_sha256: sha(new URL('../../relevia/src/services/safety.js', import.meta.url)),
  heldout_v3: score(read('data/safety_v3/heldout.jsonl')),
  development_clean: score(base),
  development_perturbed: Object.fromEntries(Object.entries(PERTURBATIONS).map(([name, f]) =>
    [name, score(base.map(c => ({ ...c, id: `${c.id}~${name}`, text: f(c.text) })))])),
};
// v3 categories, so the remaining misses are visible by failure type
const v3rows = read('data/safety_v3/heldout.jsonl');
result.heldout_v3.by_category = Object.fromEntries([...new Set(v3rows.map(r => r.category))].map(cat => {
  const rows = v3rows.filter(r => r.category === cat && r.expected_urgent !== null);
  return [cat, Object.fromEntries(Object.keys(detectors).map(d => [d, rows.filter(r =>
    (detectors[d](r.text, r.history) === 'urgent') === r.expected_urgent).length + '/' + rows.length]))];
}));

const dir = new URL('results/safety/s2-v1/', root);
const text = JSON.stringify(result, null, 2) + '\n';
if (process.argv.includes('--verify')) {
  if (readFileSync(new URL('evaluation.json', dir), 'utf8') !== text) throw Error('Recomputed S2 evidence differs');
  console.log('Verified S2 evidence without changing it');
} else {
  if (existsSync(new URL('evaluation.json', dir))) throw Error('Preserve existing results; choose a new version folder');
  mkdirSync(dir, { recursive: true });
  writeFileSync(new URL('evaluation.json', dir), text);
}
for (const split of ['heldout_v3', 'development_clean']) {
  for (const [d, m] of Object.entries(result[split].detectors)) {
    console.log(split.padEnd(18), d, `recall ${m.recall.toFixed(2)} [${m.recall_wilson95.map(x => x.toFixed(2))}]`,
      `FPR ${m.false_positive_rate.toFixed(2)}`, 'missed', m.missed.join(','), 'false alarms', m.false_alarms.join(','));
  }
}
for (const [p, r] of Object.entries(result.development_perturbed)) {
  console.log('perturbed'.padEnd(18), p.padEnd(22), Object.entries(r.detectors).map(([d, m]) => `${d} ${m.recall.toFixed(2)}/${m.false_positive_rate.toFixed(2)}`).join('  '));
}
console.log(result.heldout_v3.by_category);
