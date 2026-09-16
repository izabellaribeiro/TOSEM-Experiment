from __future__ import annotations
import argparse, subprocess, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
VENDOR=ROOT/"vendor/aqusa-core"
DATA={"PlanningPoker":"planningpoker.txt","BADCamp":"badcamp.txt","Zooniverse":"zooniverse.txt"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--project",choices=DATA); args=ap.parse_args()
    projects=[args.project] if args.project else list(DATA)
    (ROOT/"outputs/raw/AQUSA").mkdir(parents=True,exist_ok=True)
    for project in projects:
        src=ROOT/"data/processed"/DATA[project]
        dst=VENDOR/"input"/f"experiment-{DATA[project]}"
        shutil.copy2(src,dst)
        outname=f"experiment-{project.lower()}"
        cmd=[sys.executable,"aqusacore.py","-i",dst.name,"-o",outname,"-f","txt"]
        print("RUN",project," ".join(cmd))
        subprocess.run(cmd,cwd=VENDOR,check=True)
        produced=VENDOR/"output"/(outname+".txt")
        shutil.copy2(produced,ROOT/"outputs/raw/AQUSA"/(project+".txt"))
if __name__=="__main__": main()
