import json,platform,sys,datetime
from pathlib import Path
from common import sha256,load_json
ROOT=Path(__file__).resolve().parents[1]
files=[
 ROOT/'config/experiment.json',ROOT/'config/criteria.json',ROOT/'config/prompt_examples.json',
 ROOT/'prompts/system.txt',ROOT/'prompts/zero_shot.txt',ROOT/'prompts/one_shot.txt',ROOT/'prompts/few_shot.txt',
 ROOT/'ground_truth/gold_standard_qus13.csv']
manifest={
 'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'python':sys.version,'platform':platform.platform(),'config':load_json(ROOT/'config/experiment.json'),
 'sha256':{str(p.relative_to(ROOT)):sha256(p) for p in files}}
(ROOT/'results').mkdir(exist_ok=True)
(ROOT/'results/experiment_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(ROOT/'results/experiment_manifest.json')
