// Surface-perturbation stress test for the deterministic safety router (S0 and S1).
//
// Why: S1 is a set of regular expressions. Real people type "cant", "im", "wanna",
// use capitals, typos and filler. The frozen suite only has clean sentences, so its
// recall says nothing about how brittle the rules are to ordinary typing.
// Each perturbation is deterministic (seeded), applied to every labelled case in the
// frozen development and held-out suites, and scored the same way as evaluate_safety.mjs.
//
// Limits: the perturbed sentences are derived from cases that
// have already been inspected, so this is a robustness probe, not new held-out
// evidence. Labels are still agent-authored and provisional.
//
// Run:  node scripts/perturb_safety.mjs        (writes results/safety/perturbation-v1/)
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
// The probe targets frozen S1; the application now runs S2 (see evaluate_safety_s2.mjs).
import { CRISIS_RE, assessRisk } from '../detectors/s1/safety.js';

const root = new URL('../', import.meta.url);
const detectorPath = new URL('../detectors/s1/safety.js', import.meta.url);
const sha = buf => createHash('sha256').update(buf).digest('hex');
const freeze = JSON.parse(readFileSync(new URL('data/safety_v2/freeze.json', root)));
for (const name of ['development.jsonl', 'heldout.jsonl']) {
  if (sha(readFileSync(new URL('data/safety_v2/' + name, root))) !== freeze[name]) throw Error('Safety suite changed');
}
const detectorSha = sha(readFileSync(detectorPath));

import { PERTURBATIONS } from './perturbations.mjs';

function wilson(k, n) {
  if (!n) return null;
  const z = 1.959963984540054, p = k / n, den = 1 + z * z / n;
  const c = (p + z * z / (2 * n)) / den, r = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den;
  return [Math.max(0, c - r), Math.min(1, c + r)];
}

const cases = ['development', 'heldout'].flatMap(split =>
  readFileSync(new URL(`data/safety_v2/${split}.jsonl`, root), 'utf8').trim().split('\n')
    .map(l => ({ ...JSON.parse(l), split })).filter(r => r.expected_urgent !== null));

const result = {
  scope: 'Robustness probe on already-inspected synthetic cases; not held-out evidence and not clinical validation',
  detector_sha256: detectorSha, detector_matches_frozen_S1: detectorSha === freeze.detector_sha256,
  cases: cases.length, urgent_cases: cases.filter(c => c.expected_urgent).length, perturbations: {},
};
const baseline = {};
for (const [name, f] of Object.entries(PERTURBATIONS)) {
  const out = { examples: [], S0: { tp: 0, fn: 0, fp: 0, tn: 0 }, S1: { tp: 0, fn: 0, fp: 0, tn: 0 },
    S1_any_flag_on_urgent: 0, S1_lost_vs_original: [], S1_gained_vs_original: [] };
  for (const c of cases) {
    const text = f(c.text);
    const s1 = assessRisk(text, c.history).level;
    const predicted = { S0: CRISIS_RE.test(text), S1: s1 === 'urgent' };
    for (const d of ['S0', 'S1']) out[d][c.expected_urgent ? (predicted[d] ? 'tp' : 'fn') : (predicted[d] ? 'fp' : 'tn')]++;
    if (c.expected_urgent && s1 !== 'none') out.S1_any_flag_on_urgent++;
    if (name === 'original') baseline[c.id] = predicted.S1;
    else if (baseline[c.id] && !predicted.S1) out.S1_lost_vs_original.push(c.id);
    else if (!baseline[c.id] && predicted.S1) out.S1_gained_vs_original.push(c.id);
    if (out.examples.length < 2 && c.expected_urgent) out.examples.push(text);
  }
  for (const d of ['S0', 'S1']) {
    const { tp, fn, fp, tn } = out[d];
    out[d].recall = tp / (tp + fn); out[d].recall_wilson95 = wilson(tp, tp + fn);
    out[d].false_positive_rate = fp / (fp + tn); out[d].fpr_wilson95 = wilson(fp, fp + tn);
  }
  out.S1_any_flag_rate_on_urgent = out.S1_any_flag_on_urgent / result.urgent_cases;
  result.perturbations[name] = out;
}

const dir = new URL('results/safety/perturbation-v1/', root);
if (process.argv.includes('--verify')) {
  const saved = readFileSync(new URL('evaluation.json', dir), 'utf8');
  if (saved !== JSON.stringify(result, null, 2) + '\n') throw Error('Recomputed perturbation evidence differs');
  console.log('Verified perturbation-v1 evidence without changing it');
  process.exit(0);
}
if (existsSync(new URL('evaluation.json', dir))) throw Error('Preserve existing results; choose a new version folder');
mkdirSync(dir, { recursive: true });
writeFileSync(new URL('evaluation.json', dir), JSON.stringify(result, null, 2) + '\n');
console.log('detector matches frozen S1:', result.detector_matches_frozen_S1);
for (const [name, r] of Object.entries(result.perturbations)) {
  console.log(name.padEnd(22), 'S1 recall', r.S1.recall.toFixed(2), ' any-flag', r.S1_any_flag_rate_on_urgent.toFixed(2),
    ' FPR', r.S1.false_positive_rate.toFixed(2), ' S0 recall', r.S0.recall.toFixed(2), ' lost', r.S1_lost_vs_original.length);
}
