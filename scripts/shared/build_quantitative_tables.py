from __future__ import annotations
import csv,statistics
from collections import defaultdict
from pathlib import Path
from scripts.shared.paths import generated_path, metric_path, table_path
METRICS=['precision','recall','F1','specificity','accuracy','balanced_accuracy','FPR','FNR','NPV','MCC']

def read(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def fl(v):
    try:return float(v) if v not in ('',None) else None
    except:return None
def write(name,rows):
    if not rows:return
    table_path(name).parent.mkdir(parents=True,exist_ok=True)
    with open(table_path(name),'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def summarize(rows,keys):
    g=defaultdict(list)
    for r in rows:g[tuple(r.get(k,'') for k in keys)].append(r)
    out=[]
    for key,rs in sorted(g.items()):
        o=dict(zip(keys,key));o['runs']=len(rs)
        for m in ['TP','FP','FN','TN']+METRICS:
            xs=[fl(r.get(m)) for r in rs];xs=[x for x in xs if x is not None]
            o[m+'_mean']=sum(xs)/len(xs) if xs else '';o[m+'_sd']=statistics.stdev(xs) if len(xs)>1 else (0.0 if xs else '')
        out.append(o)
    return out

def main():
    e=read(metric_path('effectiveness_by_run.csv')); llm=[r for r in e if r['model']!='AQUSA']
    specs=[('overall',['prompt_profile','model'],'01_overall_by_prompt_model.csv'),('criterion',['prompt_profile','model','criterion'],'02_by_prompt_model_criterion.csv'),('dimension',['prompt_profile','model','dimension'],'03_by_prompt_model_dimension.csv'),('project',['prompt_profile','model','project'],'04_by_prompt_model_project.csv')]
    for level,keys,name in specs:write(name,summarize([r for r in llm if r['level']==level],keys))
    # Prompt-centric comparison: averages across the configured models, while retaining model-level table above as primary.
    ov=summarize([r for r in llm if r['level']=='overall'],['prompt_profile'])
    write('05_prompt_strategy_summary.csv',ov)
    # Majority-vote overall by profile/model
    maj=read(metric_path('majority_vote_metrics.csv')); write('06_majority_vote_by_prompt_model_project.csv',maj)
    var=read(metric_path('variability.csv')); write('07_variability_raw_by_prompt_model_criterion_project.csv',var)
    aq=read(metric_path('aqusa_supported5_by_run.csv')); write('08_aqusa_supported5_by_prompt_model_project_run.csv',aq)
    # Ranking within model across prompts by mean F1
    overall=read(table_path('01_overall_by_prompt_model.csv')); out=[]
    by=defaultdict(list)
    for r in overall: by[r['model']].append(r)
    for model,rs in by.items():
        rs=sorted(rs,key=lambda r:fl(r['F1_mean']) if fl(r['F1_mean']) is not None else -1,reverse=True)
        for i,r in enumerate(rs,1): out.append({'model':model,'rank':i,'prompt_profile':r['prompt_profile'],'F1_mean':r['F1_mean'],'MCC_mean':r['MCC_mean'],'balanced_accuracy_mean':r['balanced_accuracy_mean']})
    write('09_prompt_ranking_within_model.csv',out)
    table_path('README.txt').write_text('Primary comparisons are prompt_profile Ã— model. Do not average across prompt strategies when answering the prompting RQ. Use mean/sd across five runs, and treat majority vote as secondary.\n',encoding='utf-8')
    print('Built prompt-aware tables in',generated_path('results'))
if __name__=='__main__':main()
