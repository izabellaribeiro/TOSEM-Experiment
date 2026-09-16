from pathlib import Path
import csv, json
ROOT=Path(__file__).resolve().parents[2]
cfg=json.loads((ROOT/'config/experiment.json').read_text(encoding='utf-8'))
expected={'PlanningPoker':53,'BADCamp':69,'Zooniverse':60}
criteria=json.loads((ROOT/'config/criteria.json').read_text(encoding='utf-8'))['criteria']
assert len(criteria)==13
with open(ROOT/cfg['ground_truth_csv'],encoding='utf-8',newline='') as f: gt=list(csv.DictReader(f))
assert len(gt)==2366, len(gt)
for project,p in cfg['datasets'].items():
    n=len([x for x in (ROOT/p).read_text(encoding='utf-8').splitlines() if x.strip()])
    assert n==expected[project], (project,n)
    units=[r for r in gt if r['project']==project]
    assert len(units)==n*13,(project,len(units))
print('OK: 182 canonical stories, 13 QUS criteria, 2,366 Ground Truth units.')
print('OK counts:',expected)
print('AQUSA-supported criteria:',', '.join(cfg['aqusa_supported_criteria']))
