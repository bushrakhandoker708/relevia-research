// Builds SIMULATED stream traces from saved replies, for development checks of the
// release-policy replay (scripts/replay_release.mjs) before real browser traces exist.
//
// Each word is one chunk, arriving at the measured browser decode rate (5.6 tok/s,
// results/performance/browser-v1-intel) at about 1.3 tokens per word, after a fixed
// 0.23 s to the first word. Real chunk timing varies; this does not.
// The traces carry no labels, so a replay of them can measure latency, not exposure.
// The final test set (experiment_01/test-v1) is excluded: release policies must not be
// designed on test outputs.
//
//   node scripts/simulate_traces.mjs --out results/release/sim-dev-v1/traces.json
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';

const out = process.argv[process.argv.indexOf('--out') + 1];
if (!process.argv.includes('--out') || !out) throw new Error('Usage: --out <file>');
if (existsSync(out)) throw new Error(`${out} exists; results are never overwritten`);

const TOK_PER_S = 5.6, TOK_PER_WORD = 1.3, FIRST_MS = 230;
const corpora = ['experiment_01/dev-v1', 'experiment_01/dev-v2', 'experiment_01/expanded-v1',
  'performance/repeat-v1', 'lora/smoke-v1-generations', 'safety/generative-v1'];
const root = new URL('../', import.meta.url);
const traces = [];
for (const c of corpora) {
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
console.log(`${traces.length} simulated traces from ${corpora.length} corpora`);
