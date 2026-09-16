from __future__ import annotations
import csv,itertools,math,statistics
from collections import defaultdict,Counter
from pathlib import Path
from scripts.shared.common import load_json,write_csv
from scripts.shared.paths import generated_path, metric_path
ROOT=Path(__file__).resolve().parents[2]


def read_csv(path):
    with open(path,encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def safe(n,d): return n/d if d else None

def confusion(pairs):
    tp=fp=fn=tn=0
    for gt,p in pairs:
        if gt=='Violation' and p=='Violation': tp+=1
        elif gt=='No Violation' and p=='Violation': fp+=1
        elif gt=='Violation' and p=='No Violation': fn+=1
        elif gt=='No Violation' and p=='No Violation': tn+=1
    return tp,fp,fn,tn

def mcc(tp,fp,fn,tn):
    den=(tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)
    return ((tp*tn-fp*fn)/math.sqrt(den)) if den else None

def metrics(pairs):
    tp,fp,fn,tn=confusion(pairs); precision=safe(tp,tp+fp); recall=safe(tp,tp+fn); spec=safe(tn,tn+fp)
    return {'n':len(pairs),'TP':tp,'FP':fp,'FN':fn,'TN':tn,'precision':precision,'recall':recall,
            'F1':safe(2*tp,2*tp+fp+fn),'specificity':spec,'accuracy':safe(tp+tn,tp+tn+fp+fn),
            'balanced_accuracy':None if recall is None or spec is None else (recall+spec)/2,
            'FPR':safe(fp,fp+tn),'FNR':safe(fn,fn+tp),'NPV':safe(tn,tn+fn),'MCC':mcc(tp,fp,fn,tn)}

def stdev(xs): return statistics.stdev(xs) if len(xs)>1 else 0.0

def jaccard(a,b):
    u=a|b; return 1.0 if not u else len(a&b)/len(u)

def fleiss_kappa_binary(unit_run_decisions):
    if not unit_run_decisions: return None
    n=len(unit_run_decisions[0]); N=len(unit_run_decisions)
    if n<2 or any(len(x)!=n for x in unit_run_decisions): return None
    Pis=[]; total=Counter()
    for decs in unit_run_decisions:
        c=Counter(decs); total.update(decs); Pis.append((sum(v*v for v in c.values())-n)/(n*(n-1)))
    Pbar=sum(Pis)/N; pV=total['Violation']/(N*n); pN=total['No Violation']/(N*n); Pe=pV*pV+pN*pN
    return None if Pe==1 else (Pbar-Pe)/(1-Pe)

def main():
    cfg=load_json(ROOT/'config/experiment.json')
    gt=read_csv(ROOT/cfg['ground_truth_csv']); defs=load_json(ROOT/'config/criteria.json')['criteria']
    dim={c['name']:c['dimension'] for c in defs}
    gt_map={(r['project'],r['story_id'],r['qus_criterion']):r['decision'] for r in gt}
    excluded=set(cfg['binary_ground_truth_policy']['exclude_labels_from_primary_metrics'])

    llm=read_csv(generated_path('outputs/parsed/normalized/llm_predictions.csv'))
    aqusa=read_csv(generated_path('outputs/parsed/normalized/aqusa_predictions.csv')) if (generated_path('outputs/parsed/normalized/aqusa_predictions.csv')).exists() else []
    for r in aqusa:
        r['prompt_profile']='AQUSA'; r['prompt_label']='AQUSA'; r['shots']='';
    all_preds=llm+aqusa

    evaluated=[]; excluded_rows=[]
    for r in all_preds:
        g=gt_map.get((r['project'],r['story_id'],r['criterion']))
        if g is None: continue
        rr=dict(r); rr['ground_truth']=g; rr['dimension']=dim.get(r['criterion'],'')
        if g in excluded: excluded_rows.append(rr); continue
        if g in ('Violation','No Violation'): evaluated.append(rr)
    write_csv(metric_path('excluded_ground_truth_units.csv'),excluded_rows,list(excluded_rows[0]) if excluded_rows else ['model'])

    errs=[]
    for r in evaluated:
        et='FP' if r['ground_truth']=='No Violation' and r['decision']=='Violation' else ('FN' if r['ground_truth']=='Violation' and r['decision']=='No Violation' else '')
        if et: er=dict(r); er['error_type']=et; errs.append(er)
    write_csv(metric_path('error_details_fp_fn.csv'),errs,list(errs[0]) if errs else ['model'])

    metric_rows=[]
    specs=[
      ('project_criterion',['prompt_profile','model','project','run','criterion']),
      ('project',['prompt_profile','model','project','run']),
      ('project_dimension',['prompt_profile','model','project','run','dimension']),
      ('dimension',['prompt_profile','model','run','dimension']),
      ('criterion',['prompt_profile','model','run','criterion']),
      ('overall',['prompt_profile','model','run'])]
    for level,keys in specs:
        groups=defaultdict(list)
        for r in evaluated: groups[tuple(r.get(k,'') for k in keys)].append((r['ground_truth'],r['decision']))
        for key,pairs in groups.items():
            row={'level':level}; row.update(dict(zip(keys,key))); row.update(metrics(pairs)); metric_rows.append(row)
    fields=['level','prompt_profile','model','project','run','criterion','dimension','n','TP','FP','FN','TN','precision','recall','F1','specificity','accuracy','balanced_accuracy','FPR','FNR','NPV','MCC']
    write_csv(metric_path('effectiveness_by_run.csv'),metric_rows,fields)

    supported=set(cfg['aqusa_supported_criteria']); five=[r for r in evaluated if r['criterion'] in supported]
    groups=defaultdict(list)
    for r in five: groups[(r['prompt_profile'],r['model'],r['project'],r['run'])].append((r['ground_truth'],r['decision']))
    direct=[]
    for (profile,model,project,run),pairs in groups.items(): direct.append({'prompt_profile':profile,'model':model,'project':project,'run':run,**metrics(pairs)})
    write_csv(metric_path('aqusa_supported5_by_run.csv'),direct,['prompt_profile','model','project','run','n','TP','FP','FN','TN','precision','recall','F1','specificity','accuracy','balanced_accuracy','FPR','FNR','NPV','MCC'])

    llm_eval=[r for r in evaluated if r['model']!='AQUSA']
    by=defaultdict(lambda:defaultdict(dict))
    for r in llm_eval: by[(r['prompt_profile'],r['model'],r['project'],r['criterion'])][int(r['run'])][r['story_id']]=r['decision']
    var_rows=[]; freq=[]
    for (profile,model,project,criterion),runs in by.items():
        ids=sorted(set().union(*(set(v) for v in runs.values()))); run_ids=sorted(runs)
        sets={rr:{sid for sid,d in runs[rr].items() if d=='Violation'} for rr in run_ids}
        jac=[jaccard(sets[a],sets[b]) for a,b in itertools.combinations(run_ids,2)]; exact=[]; fk=[]
        for sid in ids:
            decs=[runs[rr].get(sid) for rr in run_ids]
            if all(d in ('Violation','No Violation') for d in decs):
                exact.append(len(set(decs))==1); fk.append(decs); vf=sum(d=='Violation' for d in decs)/len(decs)
                freq.append({'prompt_profile':profile,'model':model,'project':project,'criterion':criterion,'story_id':sid,'violation_frequency':vf,'flip':int(0<vf<1)})
        var_rows.append({'prompt_profile':profile,'model':model,'project':project,'criterion':criterion,'runs':len(run_ids),
            'mean_pairwise_jaccard':sum(jac)/len(jac) if jac else None,'min_pairwise_jaccard':min(jac) if jac else None,
            'unanimous_unit_rate':sum(exact)/len(exact) if exact else None,'flip_unit_rate':1-sum(exact)/len(exact) if exact else None,
            'fleiss_kappa_across_runs':fleiss_kappa_binary(fk)})
    write_csv(metric_path('variability.csv'),var_rows,['prompt_profile','model','project','criterion','runs','mean_pairwise_jaccard','min_pairwise_jaccard','unanimous_unit_rate','flip_unit_rate','fleiss_kappa_across_runs'])
    write_csv(metric_path('unit_detection_frequency.csv'),freq,['prompt_profile','model','project','criterion','story_id','violation_frequency','flip'])

    unit=defaultdict(list)
    for r in llm_eval: unit[(r['prompt_profile'],r['model'],r['project'],r['story_id'],r['criterion'],r['ground_truth'])].append(r['decision'])
    maj=[]
    for (profile,model,project,sid,crit,gt),decs in unit.items():
        if len(decs)<3: continue
        v=sum(x=='Violation' for x in decs); n=sum(x=='No Violation' for x in decs); pred='Violation' if v>n else 'No Violation'
        maj.append({'prompt_profile':profile,'model':model,'project':project,'story_id':sid,'criterion':crit,'ground_truth':gt,'prediction':pred,'votes_violation':v,'votes_no_violation':n,'runs_available':len(decs)})
    write_csv(metric_path('majority_vote_predictions.csv'),maj,['prompt_profile','model','project','story_id','criterion','ground_truth','prediction','votes_violation','votes_no_violation','runs_available'])
    mg=defaultdict(list)
    for r in maj: mg[(r['prompt_profile'],r['model'],r['project'])].append((r['ground_truth'],r['prediction']))
    mm=[]
    for (profile,model,project),pairs in mg.items(): mm.append({'prompt_profile':profile,'model':model,'project':project,**metrics(pairs)})
    write_csv(metric_path('majority_vote_metrics.csv'),mm,['prompt_profile','model','project','n','TP','FP','FN','TN','precision','recall','F1','specificity','accuracy','balanced_accuracy','FPR','FNR','NPV','MCC'])

    # run mean/sd by prompt x model, overall and project
    src=[r for r in metric_rows if r['level'] in ('project','overall') and r['model']!='AQUSA']
    gg=defaultdict(list)
    for r in src: gg[(r['level'],r['prompt_profile'],r['model'],r.get('project',''))].append(r)
    metric_names=['TP','FP','FN','TN','precision','recall','F1','specificity','accuracy','balanced_accuracy','MCC']
    summary=[]
    for (level,profile,model,project),rs in gg.items():
        row={'level':level,'prompt_profile':profile,'model':model,'project':project,'runs':len(rs)}
        for mn in metric_names:
            xs=[float(r[mn]) for r in rs if r.get(mn) not in (None,'')]
            row[mn+'_mean']=sum(xs)/len(xs) if xs else None; row[mn+'_sd']=stdev(xs) if xs else None
        summary.append(row)
    write_csv(metric_path('run_summary_mean_sd.csv'),summary,['level','prompt_profile','model','project','runs']+[x+s for x in metric_names for s in ('_mean','_sd')])

    print('Metrics written to',generated_path('results'))

if __name__=='__main__': main()
