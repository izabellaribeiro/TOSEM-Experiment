from __future__ import annotations
import json
from pathlib import Path
from scripts.shared.common import write_csv
from scripts.shared.paths import generated_path
ROOT=Path(__file__).resolve().parents[2]
FIELDS=['prompt_profile','prompt_label','shots','model','provider','project','run','story_id','criterion','decision','evidence','rationale','related_story_ids','confidence']

def main():
    rows=[]
    for p in sorted(p for profile in ('zero_shot', 'one_shot', 'few_shot') for p in (ROOT/'outputs'/'parsed'/profile).glob('*/*/run_*/*.parsed.json')):
        d=json.loads(p.read_text(encoding='utf-8')); m=d['metadata']
        for x in d['evaluations']:
            rows.append({
                'prompt_profile':m['prompt_profile'],'prompt_label':m.get('prompt_label',m['prompt_profile']),
                'shots':m.get('shots',''),'model':m['model_label'],'provider':m['provider'],
                'project':m['project'],'run':m['run'],**x
            })
    out=generated_path('outputs/parsed/normalized/llm_predictions.csv')
    write_csv(out,rows,FIELDS)
    print(f'Wrote {len(rows)} rows to {out}')

if __name__=='__main__': main()
