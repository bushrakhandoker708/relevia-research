// Deterministic text perturbations shared by perturb_safety.mjs and evaluate_safety_s2.mjs.
// tiny seeded PRNG so the typo perturbation is identical on every run
function rng(seed) {
  return () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 2 ** 32; };
}
const words = (t, f) => t.split(' ').map(f).join(' ');

export const PERTURBATIONS = {
  original: t => t,
  upper_case: t => t.toUpperCase(),
  curly_apostrophe: t => t.replace(/'/g, '’'),          // positive control: the normaliser handles this
  no_apostrophes: t => t.replace(/['’]/g, ''),         // "can't" -> "cant", "I'm" -> "Im"
  texting: t => t.replace(/\bI am\b/gi, 'im').replace(/\bI'm\b/gi, 'im').replace(/\bwant to\b/gi, 'wanna')
    .replace(/\bgoing to\b/gi, 'gonna').replace(/\byou\b/gi, 'u').replace(/\bmyself\b/gi, 'my self'),
  no_punctuation_lower: t => t.toLowerCase().replace(/[.,!?;:]/g, ''),
  filler_prefix: t => 'ok so idk how to say this but ' + t,
  extra_spaces: t => t.replace(/ /g, '   '),
  adjacent_typo: t => { const r = rng(7); return words(t, w => (w.length > 4 && r() < 0.35)
    ? w.slice(0, 2) + w[3] + w[2] + w.slice(4) : w); },
  letter_stretch: t => words(t, w => (w.length > 3 ? w.replace(/([aeiou])/i, '$1$1$1') : w)),
  leetspeak: t => words(t, w => (w.length > 3 ? w.replace(/e/g, '3').replace(/i/g, '1').replace(/o/g, '0') : w)),
  zero_width: t => t.replace(/(\w)(\w)/, '$1​$2'),
};
