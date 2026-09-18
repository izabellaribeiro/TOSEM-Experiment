"""Recover provenance of an already manually selected sample; never select cases.

The study author clarified manual stratified, coverage-oriented selection with
no random seed. Match workbook cases to individual-run normalized outputs by
project, story, criterion, prediction, evidence, rationale and related story IDs.
Cross-check both coder workbooks and final human reference. Preserve all candidate
records; a unique match is evidence within this input snapshot, not a recovered
historical selection log. Never assign a run for a multiply matched case.
"""
import json
import posixpath
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

from scripts.shared.common import sha256, write_csv
from scripts.shared.metrics import read_csv
from scripts.shared.paths import ROOT

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL_NS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
METHOD = 'manual_stratified_coverage_selection'
SAMPLE = ROOT / 'data/qualitative_sample'
FINAL = ROOT / 'results/rq4/final_adjudicated.xlsx'
PREDICTIONS = ROOT / 'outputs/parsed/normalized/llm_predictions.csv'
REFERENCE = ROOT / 'data/ground_truth/gold_standard_qus13_final.csv'


def workbook_table(path, sheet_name):
    """Read saved OOXML cell values without modifying workbooks/running macros."""
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(t.text or '' for t in item.findall('.//s:t', NS))
                       for item in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        sheets = ET.fromstring(archive.read('xl/workbook.xml')).find('s:sheets', NS)
        sheet = next(item for item in sheets if item.attrib['name'] == sheet_name)
        relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        target = next(item.attrib['Target'] for item in relationships
                      if item.attrib['Id'] == sheet.attrib[REL_NS])
        member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        rows = []
        for row in ET.fromstring(archive.read(member)).findall('s:sheetData/s:row', NS):
            values = {}
            for cell in row:
                column = ''.join(c for c in cell.attrib['r'] if c.isalpha())
                value = cell.find('s:v', NS)
                text = value.text or '' if value is not None else ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
                if cell.attrib.get('t') == 's':
                    text = strings[int(text)]
                values[column] = text
            rows.append(values)
    header = rows[0]
    return [{name: row.get(column, '') for column, name in header.items() if name}
            for row in rows[1:] if row.get('A', '')]


def matching_key(project, story, criterion, prediction, evidence, rationale, related):
    # Parse only the JSON serialization of the ID list; do not repair text/labels.
    related_ids = json.loads(related)
    if not isinstance(related_ids, list):
        raise ValueError('Expected a JSON array of related story IDs')
    return project, story, criterion, prediction, evidence, rationale, tuple(related_ids)


def case_key(row, related_column='Related Story IDs'):
    return matching_key(row['Project'], row['Story ID'], row['QUS Criterion'],
                        row['LLM Decision'], row['LLM Evidence'], row['LLM Rationale'], row[related_column])


def common_value(candidates, field):
    values = {row[field] for row in candidates}
    return next(iter(values)) if len(values) == 1 else ''


def main():
    cases = workbook_table(FINAL, 'Final Coding')
    case_ids = [row['Case ID'] for row in cases]
    if len(cases) != 30 or len(set(case_ids)) != 30:
        raise ValueError('Expected 30 distinct existing qualitative Case IDs')
    for filename in ['qualitative_evaluation_coder1.xlsx', 'qualitative_evaluation_coder2.xlsx']:
        coder = workbook_table(SAMPLE / filename, 'Evaluation')
        by_id = {row['Case ID']: row for row in coder}
        if len(coder) != 30 or set(by_id) != set(case_ids):
            raise ValueError(f'{filename}: case IDs differ from final workbook')
        for case in cases:
            row = by_id[case['Case ID']]
            if case_key(row, 'Related Story IDs (LLM)') != case_key(case) or row['Ground Truth'] != case['Ground Truth'] or row['User Story'] != case['User Story']:
                raise ValueError(f"{filename}: case contents differ for {case['Case ID']}")

    reference_rows = read_csv(REFERENCE)
    reference = {(r['project'], r['story_id'], r['qus_criterion']): r for r in reference_rows}
    if len(reference) != len(reference_rows):
        raise ValueError('Duplicate human reference keys')
    index = defaultdict(list)
    for number, row in enumerate(read_csv(PREDICTIONS), start=2):
        key = matching_key(*(row[k] for k in ['project', 'story_id', 'criterion', 'decision', 'evidence', 'rationale', 'related_story_ids']))
        index[key].append({**row, 'normalized_csv_record': number})

    manifest, candidate_rows = [], []
    quadrants = {('Violation', 'Violation'): 'TP', ('No Violation', 'No Violation'): 'TN',
                 ('No Violation', 'Violation'): 'FP', ('Violation', 'No Violation'): 'FN'}
    for case in sorted(cases, key=lambda row: row['Case ID']):
        key = case_key(case)
        gt = reference[key[:3]]
        if gt['decision'] != case['Ground Truth'] or gt['user_story'] != case['User Story']:
            raise ValueError(f"Reference disagrees with case {case['Case ID']}")
        quadrant = quadrants[(case['Ground Truth'], case['LLM Decision'])]
        if quadrant != case['Quadrant']:
            raise ValueError(f"Recorded quadrant disagrees with labels: {case['Case ID']}")
        candidates = sorted(index[key], key=lambda r: (r['model'], r['prompt_profile'], int(r['run']), r['normalized_csv_record']))
        manifest.append({
            'case_id': case['Case ID'], 'classification_quadrant': quadrant,
            'model': common_value(candidates, 'model'), 'prompt_profile': common_value(candidates, 'prompt_profile'),
            'project': case['Project'], 'story_id': case['Story ID'], 'criterion': case['QUS Criterion'],
            'run': candidates[0]['run'] if len(candidates) == 1 else '',
            'ground_truth': case['Ground Truth'], 'prediction': case['LLM Decision'],
            'selection_method': METHOD,
            'source_status': 'unique_match' if len(candidates) == 1 else 'ambiguous' if candidates else 'unresolved',
            'candidate_count': len(candidates),
        })
        for row in candidates:
            parsed = f"outputs/parsed/{row['prompt_profile']}/{row['model']}/{row['project']}/run_{int(row['run']):02d}/{row['criterion'].lower().replace(' ', '_').replace('-', '_')}.parsed.json"
            if not (ROOT / parsed).is_file():
                raise ValueError(f'Missing candidate parsed artifact: {parsed}')
            candidate_rows.append({
                'case_id': case['Case ID'], **{k: row[k] for k in ['model', 'prompt_profile', 'project', 'story_id', 'criterion', 'run']},
                'ground_truth': case['Ground Truth'], 'prediction': row['decision'],
                'normalized_csv_record': row['normalized_csv_record'], 'parsed_artifact': parsed,
            })
    if Counter(row['classification_quadrant'] for row in manifest) != {'TP': 8, 'TN': 8, 'FP': 7, 'FN': 7}:
        raise ValueError('Workbook quadrant counts differ from the author-confirmed sample')
    source_files = [FINAL, SAMPLE / 'qualitative_evaluation_coder1.xlsx', SAMPLE / 'qualitative_evaluation_coder2.xlsx', PREDICTIONS, REFERENCE]
    summary = {
        'purpose': 'Provenance recovery for an existing manually selected sample, not a sampling algorithm',
        'procedure_authority': 'Study author clarification in the repository task',
        'selection_method': METHOD, 'random_sampling': False, 'random_seed_used': False,
        'matching_fields': ['project', 'story_id', 'criterion', 'prediction', 'evidence', 'rationale', 'related_story_ids'],
        'source_sha256': {p.relative_to(ROOT).as_posix(): sha256(p) for p in source_files},
        'case_count': len(manifest), 'candidate_record_count': len(candidate_rows),
        'source_status_counts': dict(Counter(r['source_status'] for r in manifest)),
        'ambiguous_cases': [r['case_id'] for r in manifest if r['source_status'] == 'ambiguous'],
        'unresolved_cases': [r['case_id'] for r in manifest if r['source_status'] == 'unresolved'],
        'coverage': {field: dict(sorted(Counter(r[field] or 'unresolved' for r in manifest).items()))
                     for field in ['classification_quadrant', 'model', 'prompt_profile', 'project', 'criterion']},
    }
    write_csv(SAMPLE / 'sampling_manifest.csv', manifest, list(manifest[0]))
    candidate_fields = ['case_id', 'model', 'prompt_profile', 'project', 'story_id', 'criterion', 'run', 'ground_truth', 'prediction', 'normalized_csv_record', 'parsed_artifact']
    write_csv(SAMPLE / 'sampling_candidate_matches.csv', candidate_rows, candidate_fields)
    (SAMPLE / 'sampling_manifest_audit.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
