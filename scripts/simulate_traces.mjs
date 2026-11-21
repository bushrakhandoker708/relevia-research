// Builds SIMULATED stream traces from saved replies, for development checks of the
// release-policy replay (scripts/replay_release.mjs) before real browser traces exist.
//
// Each word is one chunk, arriving at the measured browser decode rate (5.6 tok/s,
// results/performance/browser-v1-intel) at about 1.3 tokens per word, after a fixed
// 0.23 s to the first word. Real chunk timing varies; this does not.
// The traces carry no labels, so a replay of them can measure latency, not exposure.
//
// Only replies to DEVELOPMENT inputs are allowed. Release policies must not be designed on
// test or held-out material. The first version of this script (kept, with its output, in
// results/release/sim-dev-v1/) excluded experiment_01/test-v1 but still read replies to
// test-only and held-out inputs: expanded-v1, safety/generative-v1 (safety_v3 held-out) and
// performance/repeat-v1 (generated on experiment_01/test.jsonl). See
// docs/REPRODUCIBILITY_AUDIT_2026-11-21.md. Each corpus is now checked against the input
// files it was generated from, and the script stops if any corpus is not development data.
//
//   node scripts/simulate_traces.mjs --out results/release/sim-dev-v2/traces.json
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';


const TOK_PER_S = 5.6, TOK_PER_WORD = 1.3, FIRST_MS = 230;
const corpora = ['experiment_01/dev-v1', 'experiment_01/dev-v2', 'lora/smoke-v1-generations'];
const root = new URL('../', import.meta.url);
const sha = (rel) => createHash('sha256').update(readFileSync(new URL(rel, root))).digest('hex');

// Input files that are development data, and ones that must never feed policy design.
const DEV_INPUTS = ['data/experiment_01/dev.jsonl', 'data/synthetic_dev.jsonl', 'data/safety_v2/development.jsonl'];
const PROTECTED_INPUTS = ['data/experiment_01/test.jsonl', 'data/experiment_01_expanded/test.jsonl',
  'data/safety_v2/heldout.jsonl', 'data/safety_v3/heldout.jsonl', 'data/safety_v4/heldout.jsonl'];
const devHashes = new Set(DEV_INPUTS.map(sha));
const protectedHashes = new Map(PROTECTED_INPUTS.map((p) => [sha(p), p]));

/** Returns why a corpus is development data, or throws if it is not (or cannot be shown to be). */
function checkCorpus(manifest, name) {
  const inputs = typeof manifest.inputs === 'string' ? manifest.inputs : null;
  const declared = manifest.data_sha256 || manifest.inputs_sha256 || (inputs ? sha(inputs) : null);
  if (declared && protectedHashes.has(declared)) throw new Error(`${name} was generated on ${protectedHashes.get(declared)}, which is test or held-out data`);
  if (inputs && PROTECTED_INPUTS.includes(inputs)) throw new Error(`${name} was generated on ${inputs}, which is test or held-out data`);
  if (declared && devHashes.has(declared)) return 'input hash matches a development file';
  if (!declared && manifest.phase === 'dev') return 'manifest phase is dev';
  throw new Error(`${name}: cannot show that its inputs are development data`);
}

// --check: confirm the allowed corpora pass and the corpora the first version used are refused.
if (process.argv.includes('--check')) {
  const read = (c) => JSON.parse(readFileSync(new URL(`results/${c}/manifest.json`, root), 'utf8'));
  for (const c of corpora) checkCorpus(read(c), c);
  for (const c of ['experiment_01/expanded-v1', 'performance/repeat-v1', 'safety/generative-v1', 'experiment_01/test-v1']) {
    let refused = false;
    try { checkCorpus(read(c), c); } catch { refused = true; }
    if (!refused) throw new Error(`${c} should have been refused`);
  }
  console.log('check passed');
  process.exit(0);
}

const out = process.argv[process.argv.indexOf('--out') + 1];
if (!process.argv.includes('--out') || !out) throw new Error('Usage: --out <file> | --check');
if (existsSync(out)) throw new Error(`${out} exists; results are never overwritten`);

const traces = [];
const provenance = {};
for (const c of corpora) {
  provenance[c] = checkCorpus(JSON.parse(readFileSync(new URL(`results/${c}/manifest.json`, root), 'utf8')), c);
  for (const line of readFileSync(new URL(`results/${c}/responses.jsonl`, root), 'utf8').trim().split('\n')) {
    const r = JSON.parse(line);
    if (r.status !== 'generated' || !r.response) continue;
    const words = r.response.split(/(?<=\s)/);
    traces.push({
      id: `${c}/${r.scenario_id || r.id}:${r.condition}`, userText: r.input_text || '',
      chunks: words.map((w, i) => [Math.round(FIRST_MS + i * 1000 * TOK_PER_WORD / TOK_PER_S), w]),
      unsafeSpans: [], appropriate: null,
    });
  }
}
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify(traces));
writeFileSync(out.replace(/.json$/, '') + '.provenance.json', JSON.stringify({ corpora: provenance, devInputs: DEV_INPUTS, protectedInputs: PROTECTED_INPUTS }, null, 2));
console.log(`${traces.length} simulated traces from ${corpora.length} corpora`);
