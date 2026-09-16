from __future__ import annotations
import csv, json, hashlib, re
from pathlib import Path
from typing import Any

SUPPORTED_AQUSA = ["Well-formed", "Atomic", "Minimal", "Unique", "Uniform"]
BINARY_LABELS = {"Violation", "No Violation"}


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_story_map(txt_path: str | Path, id_map_path: str | Path) -> list[dict]:
    lines = [x.strip() for x in Path(txt_path).read_text(encoding="utf-8").splitlines() if x.strip()]
    ids = json.loads(Path(id_map_path).read_text(encoding="utf-8"))
    if len(lines) != len(ids):
        raise ValueError(f"Story count mismatch: {txt_path}: {len(lines)} vs id map {len(ids)}")
    out=[]
    for i,(story,meta) in enumerate(zip(lines,ids),1):
        if meta["line"] != i or meta["user_story"] != story:
            raise ValueError(f"Canonical story/id-map mismatch at line {i}")
        out.append(meta)
    return out


def backlog_with_ids(stories: list[dict]) -> str:
    return "\n".join(f'{x["story_id"]}: {x["user_story"]}' for x in stories)


def extract_json_object(text: str) -> dict:
    text=text.strip()
    if text.startswith("```"):
        text=re.sub(r"^```(?:json)?\s*", "", text)
        text=re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start=text.find("{"); end=text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end+1])
        raise


def validate_evaluations(payload: dict, expected_ids: list[str], criterion: str) -> list[dict]:
    rows=payload.get("evaluations")
    if not isinstance(rows,list):
        raise ValueError("Response does not contain evaluations[]")
    seen=set(); norm=[]
    for row in rows:
        sid=row.get("story_id")
        if sid in seen: raise ValueError(f"Duplicate story_id: {sid}")
        seen.add(sid)
        if sid not in expected_ids: raise ValueError(f"Unknown story_id: {sid}")
        if row.get("criterion") != criterion: raise ValueError(f"Wrong criterion for {sid}")
        if row.get("decision") not in BINARY_LABELS: raise ValueError(f"Non-binary model decision for {sid}: {row.get('decision')}")
        norm.append({
            "story_id": sid,
            "criterion": criterion,
            "decision": row["decision"],
            "evidence": row.get("evidence", "") or "",
            "rationale": row.get("rationale", "") or "",
            "related_story_ids": row.get("related_story_ids", []) or [],
            "confidence": row.get("confidence", "") or "",
        })
    missing=[x for x in expected_ids if x not in seen]
    if missing: raise ValueError(f"Missing story IDs: {missing[:10]}")
    order={sid:i for i,sid in enumerate(expected_ids)}
    return sorted(norm,key=lambda r:order[r["story_id"]])


def write_csv(path: str | Path, rows: list[dict], fields: list[str]):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            rr=dict(r)
            for k,v in rr.items():
                if isinstance(v,(list,dict)): rr[k]=json.dumps(v,ensure_ascii=False)
            w.writerow({k:rr.get(k,"") for k in fields})
