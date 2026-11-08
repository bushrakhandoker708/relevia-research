// Evaluate routing separately from response quality. Labels are provisional.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
// S1 is evaluated from its frozen copy so the app can move on to S2 without breaking this evidence.
import { CRISIS_RE, assessRisk } from '../detectors/s1/safety.js';
const root = new URL('../', import.meta.url);
const hash = path => createHash('sha256').update(readFileSync(path)).digest('hex');
const freeze=JSON.parse(readFileSync(new URL('data/safety_v2/freeze.json',root)));
for(const name of ['development.jsonl','heldout.jsonl']) {
  if(hash(new URL('data/safety_v2/'+name,root))!==freeze[name])throw Error('Safety suite changed');
}
if(hash(new URL('../detectors/s1/safety.js',import.meta.url))!==freeze.detector_sha256)throw Error('Detector differs from frozen S1');
function estimate(success,total) {
  if(!total)return {value:null,denominator:0,wilson95:null};
  const p=success/total,z=1.95996398454,den=1+z*z/total;
  const centre=(p+z*z/(2*total))/den;
  const radius=z*Math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den;
  return {value:p,denominator:total,wilson95:[centre-radius,centre+radius]};
}
const result={scope:'Agent-authored synthetic routing evaluation; not clinical validation',splits:{}};
for(const split of ['development','heldout']) {
  const input=readFileSync(new URL(`data/safety_v2/${split}.jsonl`,root),'utf8').trim().split('\n').map(x=>JSON.parse(x));
  const rows=input.map(row=>({...row,S0:CRISIS_RE.test(row.text),S1:assessRisk(row.text,row.history)}));
  const scores={};
  for(const detector of ['S0','S1']) {
    const confusion={tp:0,fp:0,tn:0,fn:0};
    for(const row of rows.filter(r=>r.expected_urgent!==null)) {
      const predicted=detector==='S0'?row.S0:row.S1.level==='urgent';
      confusion[row.expected_urgent?(predicted?'tp':'fn'):(predicted?'fp':'tn')]++;
    }
    const {tp,fp,tn,fn}=confusion;
    scores[detector]={confusion,precision:estimate(tp,tp+fp),recall:estimate(tp,tp+fn),specificity:estimate(tn,tn+fp),
      false_positive_rate:estimate(fp,fp+tn),false_negative_rate:estimate(fn,fn+tp)};
  }
  result.splits[split]={scores,rows,ambiguous_excluded:rows.filter(r=>r.expected_urgent===null).length,
    check_in_count:rows.filter(r=>r.S1.level==='check_in').length};
}
const dir=new URL('results/safety/s1-v1/',root);
if(process.argv.includes('--verify')) {
  const saved=JSON.parse(readFileSync(new URL('evaluation.json',dir),'utf8'));
  if(JSON.stringify(saved)!==JSON.stringify(result))throw Error('Recomputed safety evidence differs');
  console.log('Verified frozen S1 evidence without changing original results');
} else {
  if(existsSync(new URL('evaluation.json',dir)))throw Error('Preserve existing experiment; choose a new version');
  mkdirSync(dir,{recursive:true});writeFileSync(new URL('evaluation.json',dir),JSON.stringify(result,null,2)+'\n');
}
for(const [split,data] of Object.entries(result.splits))console.log(split,JSON.stringify(data.scores));
