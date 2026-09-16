from __future__ import annotations
import json
from pathlib import Path
from common import write_csv
ROOT=Path(__file__).resolve().parents[1]
FIELDS=['prompt_profile','prompt_label','shots','model','provider','project','run','story_id','criterion','decision','evidence','rationale','related_story_ids','confidence']

def main():
    rows=[]
    for p in ROOT.glob('results/raw/*/*/*/run_*/*.parsed.json'):
        d=json.loads(p.read_text(encoding='utf-8')); m=d['metadata']
        for x in d['evaluations']:
            rows.append({
                'prompt_profile':m['prompt_profile'],'prompt_label':m.get('prompt_label',m['prompt_profile']),
                'shots':m.get('shots',''),'model':m['model_label'],'provider':m['provider'],
                'project':m['project'],'run':m['run'],**x
            })
    out=ROOT/'results/normalized/llm_predictions.csv'
    write_csv(out,rows,FIELDS)
    print(f'Wrote {len(rows)} rows to {out}')

if __name__=='__main__': main()
