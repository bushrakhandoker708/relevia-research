// Over-routing check on human-written text. The EmpatheticDialogues validation prompts
// were written by crowd workers describing everyday emotional situations, not by the
// author of S3. Most contain no current risk, so every urgent or emergency route is a
// candidate false alarm to read by hand. Some prompts do describe real grief or past
// events, so a route is not automatically wrong.
//
// The dataset is CC BY-NC 4.0 and gitignored, so only IDs and counts are written.
// Run: node scripts/scan_s3_false_alarms.mjs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import * as S2 from '../detectors/s2/safety.js';
import * as S3 from '../../relevia/src/services/safetyS3.js';

const root = new URL('../', import.meta.url);
const rows = readFileSync(new URL('data/processed/' + (process.argv.includes('--dev') ? 'dev' : 'val') + '.jsonl', root), 'utf8').trim().split('\n').map(l => JSON.parse(l));
const tally = { S2: { urgent: 0, check_in: 0, none: 0 }, S3: { emergency: 0, urgent: 0, check_in: 0, none: 0 } };
const routed = [];
for (const r of rows) {
  const s2 = S2.assessRisk(r.prompt).level;
  const s3 = S3.assessRisk(r.prompt).tier;
  tally.S2[s2]++; tally.S3[s3]++;
  if (s2 !== 'none' || s3 !== 'none') routed.push({ id: r.id, emotion: r.emotion, s2, s3, reason: S3.assessRisk(r.prompt).reason });
}
const out = { scope: 'Over-routing scan on EmpatheticDialogues ' + (process.argv.includes('--dev') ? 'DEV prompts, run once as a held-out check' : 'validation prompts') + ' (single message, no history); ids only',
  n: rows.length, tally, routed };
mkdirSync(new URL('results/safety/s3-v1-ed-scan/', root), { recursive: true });
writeFileSync(new URL('results/safety/s3-v1-ed-scan/' + (process.argv.includes('--dev') ? 'dev_heldout' : 'val_after_fix') + '.json', root), JSON.stringify(out, null, 2) + '\n');
console.log(JSON.stringify({ n: out.n, tally }, null, 1));
// local review only (not written to disk)
if (process.argv.includes('--show')) for (const r of routed) console.log(r.id, r.s2, r.s3, r.reason, '|', rows.find(x => x.id === r.id).prompt.slice(0, 160));
