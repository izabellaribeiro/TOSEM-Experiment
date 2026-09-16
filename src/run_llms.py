from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from common import (
    load_json,
    read_story_map,
    backlog_with_ids,
    extract_json_object,
    validate_evaluations,
)
from providers import call

ROOT = Path(__file__).resolve().parents[1]


def render(template: str, mapping: dict[str, str]) -> str:
    for k, v in mapping.items():
        template = template.replace("{{" + k + "}}", str(v))
    return template


def demo_to_text(demo: dict, criterion_name: str) -> str:
    lines=[]
    context=demo.get('context') or []
    if context:
        lines.append('Demo context:')
        for x in context:
            lines.append(f'{x["story_id"]}: {x["story"]}')
    lines.append(f'Target: {demo["story_id"]}: {demo["story"]}')
    payload={
        'story_id':demo['story_id'],
        'criterion':criterion_name,
        'decision':demo['decision'],
        'evidence':demo.get('evidence',''),
        'rationale':demo.get('rationale',''),
        'related_story_ids':demo.get('related_story_ids',[]),
        'confidence':demo.get('confidence','High'),
    }
    lines.append('Expected evaluation:')
    lines.append(json.dumps(payload, ensure_ascii=False))
    return '\n'.join(lines)


def render_demos(examples: dict, criterion_name: str, key: str) -> str:
    demos=examples[criterion_name][key]
    return '\n\n'.join(
        f'Example {i}:\n{demo_to_text(d, criterion_name)}'
        for i,d in enumerate(demos,1)
    )


def is_completed_result_valid(parsed_path: Path, project: str, criterion: str, run: int,
                              prompt_profile: str, expected_story_count: int) -> bool:
    if not parsed_path.exists():
        return False
    try:
        existing=json.loads(parsed_path.read_text(encoding='utf-8'))
        metadata=existing.get('metadata',{})
        evaluations=existing.get('evaluations',[])
        return (
            metadata.get('project')==project
            and metadata.get('criterion')==criterion
            and metadata.get('run')==run
            and metadata.get('prompt_profile')==prompt_profile
            and isinstance(evaluations,list)
            and len(evaluations)==expected_story_count
        )
    except Exception:
        return False


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--config',default=str(ROOT/'config/experiment.json'))
    ap.add_argument('--provider')
    ap.add_argument('--model')
    ap.add_argument('--project')
    ap.add_argument('--criterion')
    ap.add_argument('--prompt-profile', choices=['zero_shot','one_shot','few_shot'])
    ap.add_argument('--run',type=int)
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()

    cfg=load_json(args.config)
    crit_cfg=load_json(ROOT/'config/criteria.json')['criteria']
    examples=load_json(ROOT/'config/prompt_examples.json')
    system=(ROOT/'prompts/system.txt').read_text(encoding='utf-8')

    criteria=[c for c in crit_cfg if not args.criterion or c['name']==args.criterion]
    models=[m for m in cfg['models'] if (not args.provider or m['provider']==args.provider) and (not args.model or m['model']==args.model)]
    projects=[p for p in cfg['datasets'] if not args.project or p==args.project]
    profiles=[p for p in cfg['prompt_profiles'] if not args.prompt_profile or p['id']==args.prompt_profile]
    runs=[args.run] if args.run else list(range(1,cfg['runs_per_condition']+1))

    for profile in profiles:
        profile_id=profile['id']
        user_template=(ROOT/profile['template']).read_text(encoding='utf-8')
        print('\n'+'#'*80)
        print(f'PROMPT PROFILE: {profile["label"]} ({profile_id})')
        print('#'*80)

        for project in projects:
            txt=ROOT/cfg['datasets'][project]
            idmap=txt.with_name(txt.stem+'_id_map.json')
            stories=read_story_map(txt,idmap)
            ids=[s['story_id'] for s in stories]
            backlog=backlog_with_ids(stories)

            for criterion_config in criteria:
                criterion_name=criterion_config['name']
                mapping={
                    'criterion_name':criterion_name,
                    'dimension':criterion_config['dimension'],
                    'scope':criterion_config['scope'],
                    'definition':criterion_config['definition'],
                    'decision_rule':criterion_config['decision_rule'],
                    'project_name':project,
                    'backlog_with_ids':backlog,
                    'story_count':len(stories),
                    'one_shot_demo':render_demos(examples,criterion_name,'one_shot'),
                    'few_shot_demos':render_demos(examples,criterion_name,'few_shot'),
                }
                prompt=render(user_template,mapping)

                for model_config in models:
                    provider=model_config['provider']; model=model_config['model']; model_label=model_config['label']; request_options=model_config.get('request_options',{})
                    for run in runs:
                        base=ROOT/'results'/'raw'/profile_id/model_label/project/f'run_{run:02d}'
                        base.mkdir(parents=True,exist_ok=True)
                        slug=criterion_name.lower().replace(' ','_').replace('-','_')
                        request_path=base/f'{slug}.request.json'
                        response_path=base/f'{slug}.response.json'
                        parsed_path=base/f'{slug}.parsed.json'
                        error_path=base/f'{slug}.error.txt'

                        if not args.dry_run and is_completed_result_valid(parsed_path,project,criterion_name,run,profile_id,len(stories)):
                            print('SKIP',profile_id,model_label,project,run,criterion_name,'(already completed)')
                            continue

                        if args.dry_run:
                            dry_request={'prompt_profile':profile_id,'provider':provider,'model':model,'temperature':None if request_options.get('omit_temperature') else cfg['temperature'],'request_options':request_options,'system':system,'user':prompt}
                            request_path.write_text(json.dumps(dry_request,ensure_ascii=False,indent=2),encoding='utf-8')
                            print('DRY',profile_id,model_label,project,run,criterion_name)
                            continue

                        start=time.time()
                        try:
                            print('RUN',profile_id,model_label,project,run,criterion_name)
                            req,raw,text=call(provider,model,system,prompt,cfg['temperature'],request_options=request_options)
                            request_path.write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
                            response_path.write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding='utf-8')
                            payload=extract_json_object(text)
                            if 'evaluations' not in payload or not isinstance(payload['evaluations'],list):
                                raise ValueError("Response does not contain a valid 'evaluations' list")
                            for evaluation in payload['evaluations']:
                                evaluation['criterion']=criterion_name
                            rows=validate_evaluations(payload,ids,criterion_name)
                            elapsed=round(time.time()-start,3)
                            output={'metadata':{
                                'prompt_profile':profile_id,'prompt_label':profile['label'],'shots':profile['shots'],
                                'provider':provider,'model_requested':model,'model_label':model_label,
                                'project':project,'criterion':criterion_name,'run':run,'temperature':None if request_options.get('omit_temperature') else cfg['temperature'],
                                'elapsed_seconds':elapsed,
                            },'evaluations':rows}
                            parsed_path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
                            if error_path.exists(): error_path.unlink()
                            print('OK',profile_id,model_label,project,run,criterion_name,f'({elapsed}s)')
                        except Exception as error:
                            elapsed=round(time.time()-start,3)
                            error_path.write_text(repr(error),encoding='utf-8')
                            print('ERROR',profile_id,model_label,project,run,criterion_name,repr(error),f'({elapsed}s)')

if __name__=='__main__':
    main()
