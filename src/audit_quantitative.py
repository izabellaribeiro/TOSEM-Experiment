from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read_csv(p):
    with open(p,encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def main():
    cfg=json.load(open(ROOT/'config/experiment.json',encoding='utf-8'))
    llm=read_csv(ROOT/'results/normalized/llm_predictions.csv')
    expected_models={m['label'] for m in cfg['models']}; expected_profiles={p['id'] for p in cfg['prompt_profiles']}
    projects={'PlanningPoker':53,'BADCamp':69,'Zooniverse':60}; criteria=13; runs=set(range(1,cfg['runs_per_condition']+1))
    expected=len(expected_models)*len(expected_profiles)*sum(projects.values())*criteria*len(runs)
    checks=[]
    checks.append(('row_count',len(llm)==expected,f'{len(llm):,} / expected {expected:,}'))
    checks.append(('profiles',{r['prompt_profile'] for r in llm}==expected_profiles,str(sorted({r['prompt_profile'] for r in llm}))))
    checks.append(('models',{r['model'] for r in llm}==expected_models,str(sorted({r['model'] for r in llm}))))
    keys=Counter((r['prompt_profile'],r['model'],r['project'],r['run'],r['story_id'],r['criterion']) for r in llm)
    checks.append(('duplicate_keys',not any(v>1 for v in keys.values()),f'{sum(v>1 for v in keys.values())} duplicates'))
    bad=[]; grouped=defaultdict(set)
    for r in llm: grouped[(r['prompt_profile'],r['model'],r['project'],r['criterion'])].add(int(r['run']))
    for k,v in grouped.items():
        if v!=runs: bad.append((k,sorted(v)))
    checks.append(('runs',not bad,f'{len(bad)} incomplete conditions'))
    result='PASS' if all(x[1] for x in checks) else 'FAIL'
    print('='*80); print('QUS-13 × 3 PROMPTS AUDIT'); print('='*80)
    for name,ok,msg in checks: print(('PASS' if ok else 'FAIL'),name,msg)
    print('\nAUDIT RESULT:',result)
    out={'result':result,'expected_rows':expected,'found_rows':len(llm),'checks':[{'name':n,'pass':o,'message':m} for n,o,m in checks]}
    (ROOT/'results/audit').mkdir(parents=True,exist_ok=True)
    (ROOT/'results/audit/audit_summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    if result!='PASS': raise SystemExit(1)

if __name__=='__main__': main()
