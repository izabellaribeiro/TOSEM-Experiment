from __future__ import annotations
import re, json
from pathlib import Path
from common import load_json, write_csv, SUPPORTED_AQUSA
ROOT=Path(__file__).resolve().parents[1]
MAP={"well_formed":"Well-formed","atomic":"Atomic","minimal":"Minimal","unique":"Unique","uniform":"Uniform"}
PROJECT_FILES={"PlanningPoker":"planningpoker","BADCamp":"badcamp","Zooniverse":"zooniverse"}
FIELDS=["model","provider","project","run","story_id","criterion","decision","evidence","rationale","related_story_ids","confidence"]
PAT=re.compile(r'Story #(\d+): "(.*?)"\n\s+Defect type: ([^.\n]+)\.([^\n]+)\n\s+Message: (.*?)(?=\nStory #|\Z)',re.S)

def main():
    rows=[]
    for project,stem in PROJECT_FILES.items():
        raw_path=ROOT/"results/raw/AQUSA"/(project+".txt")
        if not raw_path.exists():
            print("Missing",raw_path); continue
        idmap=json.loads((ROOT/"data/canonical"/(stem+"_id_map.json")).read_text(encoding="utf-8"))
        line_to_id={x["line"]:x["story_id"] for x in idmap}
        defects={}
        text=raw_path.read_text(encoding="utf-8",errors="replace")
        for num,story,kind,subkind,msg in PAT.findall(text):
            crit=MAP.get(kind.strip())
            if not crit: continue
            sid=line_to_id[int(num)]
            defects.setdefault((sid,crit),[]).append({"subkind":subkind.strip(),"message":msg.strip()})
        for x in idmap:
            sid=x["story_id"]
            for crit in SUPPORTED_AQUSA:
                d=defects.get((sid,crit),[])
                rows.append({"model":"AQUSA","provider":"rule-based","project":project,"run":1,"story_id":sid,"criterion":crit,"decision":"Violation" if d else "No Violation","evidence":"","rationale":" | ".join(z["subkind"]+": "+z["message"] for z in d),"related_story_ids":[],"confidence":"Deterministic"})
    out=ROOT/"results/normalized/aq usa_predictions.csv".replace(" ","")
    write_csv(out,rows,FIELDS); print(f"Wrote {len(rows)} rows to {out}")
if __name__=="__main__": main()
