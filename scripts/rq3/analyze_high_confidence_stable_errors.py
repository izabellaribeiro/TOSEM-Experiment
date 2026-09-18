"""Audit high-confidence, stable, but incorrect individual-run predictions.

Unit: model x prompt_profile x project x story_id x QUS criterion. A qualifying
unit has exactly five distinct configured runs (1--5), five unanimous binary
predictions, a unanimous prediction different from its human binary reference,
and confidence exactly 'High' in every run. Stability means unanimity, never
majority voting. Labels/confidence are compared literally, without imputation,
case folding or whitespace repair. Aggregated majority-vote data is not input.

Expected units are derived from configured models/profiles, canonical story IDs
and criteria, so entirely absent units are diagnosed alongside incomplete and
duplicate-run units. Missing/ambiguous references and malformed labels are
excluded explicitly. The manuscript's 1,910 is a comparison, not a target fitted
by the analysis. All generated artifacts use the separate reproduction root.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

from scripts.shared.common import BINARY_LABELS, load_json, read_story_map, sha256, write_csv
from scripts.shared.metrics import read_csv
from scripts.shared.paths import ROOT, generated_path, output_root

EXPECTED_TOTAL = 1910
EXPECTED_RUNS = {'1', '2', '3', '4', '5'}
CONFIDENCE_LABELS = {'High', 'Moderate', 'Low'}
KEY = ['model', 'prompt_profile', 'project', 'story_id', 'criterion']
PREFIX = 'high_confidence_stable_incorrect'
FIELDS = KEY + [
    'dimension', 'ground_truth', 'unanimous_prediction', 'number_of_runs',
    'distinct_runs', 'run_ids', 'missing_runs', 'duplicate_runs',
    'high_confidence_runs', 'all_runs_high_confidence', 'complete_run_structure',
    'stable', 'incorrect', 'high_confidence_stable_incorrect',
    'prediction_counts', 'confidence_counts', 'exclusion_reasons',
]


def load_table(path, required):
    """Reuse the existing CSV reader after checking headers, even for empty CSVs."""
    with path.open(encoding='utf-8-sig', newline='') as handle:
        headers = next(csv.reader(handle), [])
    missing = set(required) - set(headers)
    if missing or len(headers) != len(set(headers)):
        raise ValueError(f'{path}: invalid schema; missing columns={sorted(missing)}; '
                         'headers must be unique. Input must contain individual runs.')
    rows = read_csv(path)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f'{path}: malformed CSV row length; no data was silently dropped.')
    return rows


def expected_design(config, criteria):
    if config['runs_per_condition'] != 5:
        raise ValueError('This analysis requires exactly five runs; configuration differs.')
    references = set()
    for project, relative in config['datasets'].items():
        text = ROOT / relative
        stories = read_story_map(text, text.with_name(text.stem + '_id_map.json'))
        for story, criterion in product(stories, criteria):
            references.add((project, story['story_id'], criterion['name']))
    models = [model['label'] for model in config['models']]
    profiles = [profile['id'] for profile in config['prompt_profiles']]
    return {(model, profile, *ref) for model, profile, ref in product(models, profiles, references)}


def analyze(predictions, ground_truth, expected_units, dimensions):
    """Return one audit record per expected or observed unit, with exclusions."""
    grouped = defaultdict(list)
    for row in predictions:
        grouped[tuple(row[key] for key in KEY)].append(row)
    references = defaultdict(list)
    for row in ground_truth:
        references[(row['project'], row['story_id'], row['qus_criterion'])].append(row['decision'])

    audited = []
    for key in sorted(expected_units | set(grouped), key=lambda k: (k[0], k[1], k[2], k[4], k[3])):
        rows = grouped[key]
        runs = Counter(row['run'] for row in rows)
        decisions = Counter(row['decision'] for row in rows)
        confidence = Counter(row['confidence'] for row in rows)
        labels = references.get(key[2:], [])
        reference = labels[0] if len(labels) == 1 else ''
        complete = len(rows) == 5 and set(runs) == EXPECTED_RUNS and all(n == 1 for n in runs.values())
        reasons = []
        if key not in expected_units:
            reasons.append('unexpected_unit')
        if len(rows) != 5:
            reasons.append('fewer_than_five_runs' if len(rows) < 5 else 'more_than_five_runs')
        if set(runs) != EXPECTED_RUNS:
            reasons.append('missing_or_unexpected_run_ids')
        if any(n > 1 for n in runs.values()):
            reasons.append('duplicate_run_ids')
        if not labels:
            reasons.append('missing_ground_truth')
        elif len(labels) != 1:
            reasons.append('duplicate_ground_truth')
        elif reference not in BINARY_LABELS:
            reasons.append('nonbinary_ground_truth')
        if set(decisions) - BINARY_LABELS:
            reasons.append('invalid_prediction_label')
        if set(confidence) - CONFIDENCE_LABELS:
            reasons.append('missing_or_invalid_confidence')

        stable = int(len(decisions) == 1) if complete and not (set(decisions) - BINARY_LABELS) else ''
        unanimous = next(iter(decisions)) if stable == 1 else ''
        incorrect = int(unanimous != reference) if stable == 1 and len(labels) == 1 and reference in BINARY_LABELS else ''
        all_high = int(complete and confidence['High'] == 5)
        qualifies = int(not reasons and stable == 1 and incorrect == 1 and all_high == 1)
        audited.append({
            **dict(zip(KEY, key)), 'dimension': dimensions.get(key[-1], ''),
            'ground_truth': reference, 'unanimous_prediction': unanimous,
            'number_of_runs': len(rows), 'distinct_runs': len(runs), 'run_ids': sorted(runs),
            'missing_runs': sorted(EXPECTED_RUNS - set(runs)),
            'duplicate_runs': sorted(run for run, n in runs.items() if n > 1),
            'high_confidence_runs': confidence['High'], 'all_runs_high_confidence': all_high,
            'complete_run_structure': int(complete), 'stable': stable, 'incorrect': incorrect,
            'high_confidence_stable_incorrect': qualifies,
            'prediction_counts': dict(sorted(decisions.items())),
            'confidence_counts': dict(sorted(confidence.items())), 'exclusion_reasons': reasons,
        })
    return audited


def percentage(count, total):
    return 100 * count / total if total else ''


def aggregate(qualifying, columns, levels):
    counts = Counter(tuple(row[column] for column in columns) for row in qualifying)
    model_totals = Counter(row['model'] for row in qualifying)
    result = []
    for key in sorted(product(*levels)):
        count = counts[key]
        row = {**dict(zip(columns, key)), 'count': count}
        if columns == ['model', 'criterion']:
            row['percentage_within_model'] = percentage(count, model_totals[key[0]])
        row['percentage_of_total'] = percentage(count, len(qualifying))
        result.append(row)
    return result


def run_analysis(input_path=None, ground_truth_path=None):
    config = load_json(ROOT / 'config/experiment.json')
    criteria = load_json(ROOT / 'config/criteria.json')['criteria']
    expected = expected_design(config, criteria)
    input_path = Path(input_path or ROOT / 'outputs/parsed/normalized/llm_predictions.csv').resolve()
    ground_truth_path = Path(ground_truth_path or ROOT / config['ground_truth_csv']).resolve()
    predictions = load_table(input_path, KEY + ['run', 'decision', 'confidence'])
    ground_truth = load_table(ground_truth_path, ['project', 'story_id', 'qus_criterion', 'decision'])
    audited = analyze(predictions, ground_truth, expected, {c['name']: c['dimension'] for c in criteria})
    qualifying = [row for row in audited if row['high_confidence_stable_incorrect']]
    excluded = [row for row in audited if row['exclusion_reasons']]
    evaluated = [row for row in audited if not row['exclusion_reasons']]
    expected_audit = [row for row in audited if tuple(row[k] for k in KEY) in expected]
    reference_keys = {(k[2], k[3], k[4]) for k in expected}
    extra_references = sorted({(r['project'], r['story_id'], r['qus_criterion']) for r in ground_truth} - reference_keys)
    summary = {
        'input': str(input_path), 'input_sha256': sha256(input_path),
        'ground_truth': str(ground_truth_path), 'ground_truth_sha256': sha256(ground_truth_path),
        'expected_units': len(expected), 'observed_prediction_rows': len(predictions),
        'observed_units': len({tuple(r[k] for k in KEY) for r in predictions}),
        'complete_run_structure_units': sum(r['complete_run_structure'] for r in expected_audit),
        'complete_units_evaluated': len(evaluated),
        'incomplete_units': sum(not r['complete_run_structure'] for r in expected_audit),
        'entirely_missing_units': sum(r['number_of_runs'] == 0 for r in expected_audit),
        'excluded_units': len(excluded),
        'exclusion_reason_counts': dict(sorted(Counter(reason for r in excluded for reason in r['exclusion_reasons']).items())),
        'unexpected_ground_truth_keys': extra_references,
        'confidence_value_counts': dict(sorted(Counter(r['confidence'] for r in predictions).items())),
        'stable_units': sum(r['stable'] == 1 for r in evaluated),
        'stable_incorrect_units': sum(r['stable'] == 1 and r['incorrect'] == 1 for r in evaluated),
        'high_confidence_stable_incorrect_units': len(qualifying),
        'expected_manuscript_value': EXPECTED_TOTAL,
        'difference': len(qualifying) - EXPECTED_TOTAL,
        'status': 'MATCH' if len(qualifying) == EXPECTED_TOTAL else 'MISMATCH',
        'data_quality_status': 'ISSUES' if excluded or extra_references else 'PASS',
    }
    destinations = {
        generated_path(f'results/rq3/metrics/{PREFIX}_units.csv'): (qualifying, FIELDS),
        generated_path(f'results/rq3/metrics/{PREFIX}_all_units_audit.csv'): (audited, FIELDS),
        generated_path(f'results/rq3/metrics/{PREFIX}_excluded_units.csv'): (excluded, FIELDS),
    }
    models = sorted(m['label'] for m in config['models'])
    criterion_names = sorted(c['name'] for c in criteria)
    tables = [
        ('model', ['model'], [models]),
        ('criterion', ['criterion'], [criterion_names]),
        ('model_criterion', ['model', 'criterion'], [models, criterion_names]),
        ('prompt', ['prompt_profile'], [sorted(p['id'] for p in config['prompt_profiles'])]),
        ('project', ['project'], [sorted(config['datasets'])]),
    ]
    for suffix, columns, levels in tables:
        rows = aggregate(qualifying, columns, levels)
        fields = columns + ['count'] + (['percentage_within_model'] if suffix == 'model_criterion' else []) + ['percentage_of_total']
        destinations[generated_path(f'results/rq3/tables/{PREFIX}_by_{suffix}.csv')] = (rows, fields)
    summary_path = generated_path(f'results/rq3/metrics/{PREFIX}_audit_summary.json')
    # Custom input paths must never alias any generated file.
    for destination in [*destinations, summary_path]:
        if destination.resolve() in (input_path, ground_truth_path):
            raise ValueError(f'Output would overwrite an input: {destination}')
    for destination, (rows, fields) in destinations.items():
        write_csv(destination, rows, fields)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print('RQ3 high-confidence stable incorrect audit\n' + '-' * 42)
    for label, name in [
        ('Complete 5-run units', 'complete_units_evaluated'), ('Incomplete units', 'incomplete_units'),
        ('Excluded units (all reasons)', 'excluded_units'), ('Stable units', 'stable_units'),
        ('Stable incorrect units', 'stable_incorrect_units'),
        ('High-confidence stable incorrect units', 'high_confidence_stable_incorrect_units'),
        ('Expected manuscript value', 'expected_manuscript_value'), ('Status', 'status'),
        ('Data quality', 'data_quality_status'),
    ]:
        print(f'{label}: {summary[name]}')
    if summary['status'] == 'MISMATCH':
        print(f"WARNING: manuscript count not reproduced. Difference: {summary['difference']:+d}")
        print('Possible sources to investigate (not assumed causes): input/reference version, '
              'missing or duplicate runs, invalid labels/confidence, or a different original counting definition.')
        print('Inspect the full unit audit, excluded units, and summary; the count has not been adjusted.')
    if summary['data_quality_status'] != 'PASS':
        print('WARNING: input quality issues are recorded in the excluded-unit CSV and audit summary.')
    print('Output root:', output_root())
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='Individual-run normalized predictions; defaults to preserved LLM CSV.')
    parser.add_argument('--ground-truth', type=Path, help='Human reference CSV; defaults to the configured final reference.')
    parser.add_argument('--output-root', type=Path, help='Separate reproduction root; otherwise use shared path defaults.')
    args = parser.parse_args()
    if args.output_root:
        os.environ['TOSEM_OUTPUT_ROOT'] = str(args.output_root.resolve())
    output_root()  # Reject protected locations before writing anything.
    summary = run_analysis(args.input, args.ground_truth)
    # Emit diagnostics first, then make a mismatch or invalid input visible to automation.
    if summary['status'] != 'MATCH' or summary['data_quality_status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
