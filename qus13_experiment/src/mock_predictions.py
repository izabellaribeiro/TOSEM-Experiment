"""Creates deterministic mock predictions equal to the binary Ground Truth for pipeline testing only."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with open(ROOT/'ground_truth/gold_standard_qus13.csv',encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
by={}
for r in rows:
    if r['decision'] not in ('Violation','No Violation'): continue
    by.setdefault((r['project'],r['qus_criterion']),[]).append(r)
for (project,criterion),rs in by.items():
    base=ROOT/'results/raw/MOCK'/project/'run_01'; base.mkdir(parents=True,exist_ok=True)
    slug=criterion.lower().replace(' ','_').replace('-','_')
    out={'metadata':{'provider':'mock','model_requested':'mock','model_label':'MOCK','project':project,'criterion':criterion,'run':1,'temperature':0},'evaluations':[]}
    # This mock intentionally cannot satisfy missing binary GT rows; it is only for metrics smoke tests if desired.
    for r in rs:
        out['evaluations'].append({'story_id':r['story_id'],'criterion':criterion,'decision':r['decision'],'evidence':'','rationale':'mock','related_story_ids':[],'confidence':'High'})
    (base/f'{slug}.parsed.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Mock files created under results/raw/MOCK. Do not use them in research results.')
