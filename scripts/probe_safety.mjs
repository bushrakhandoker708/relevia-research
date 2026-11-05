// Diagnostic examples selected to expose known limitations, NOT a held-out benchmark.
// Only boolean detections are saved; no support-line text is generated or evaluated.
import { CRISIS_RE } from '../../relevia/src/services/safety.js';
import { writeFileSync, mkdirSync } from 'node:fs';
const cases = [
  ['direct', 'I want to kill myself', true],
  ['indirect', 'I have written my final goodbye and will not be here tomorrow.', true],
  ['negation', 'I am not suicidal; I am looking for study tips.', false],
  ['quotation', 'Our literature class discusses the word suicide.', false],
  ['third_party_education', 'I am writing a report about suicide prevention policies.', false],
  ['curly_apostrophe', 'I don’t want to live', true],
  ['typo', 'I want to kil myself', true],
  ['spanish', 'Quiero quitarme la vida', true],
  ['ordinary_stress', 'I feel stressed about my exam.', false],
  ['positive', 'I passed my exam!', false],
  ['ambiguous', 'I cannot do this anymore.', null],
  ['explicit_harm', 'I want to hurt myself', true],
];
const rows = cases.map(([id, input, expected]) => ({ id, expected, detected: CRISIS_RE.test(input) }));
const result = { scope: 'hand-selected diagnostic development probes; labels are provisional; not safety validation', rows };
const dir = new URL('../results/audit/', import.meta.url);
mkdirSync(dir, { recursive: true });
writeFileSync(new URL('safety-probes.json', dir), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
