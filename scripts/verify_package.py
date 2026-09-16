"""Verify artifact preservation and compare existing CSVs; not a study analysis."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def csv_contents(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        rows = Counter(tuple(sorted(row.items())) for row in reader)
    return fields, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reproduced-root', type=Path)
    args = parser.parse_args()
    inventory = ROOT / 'docs/provenance/artifact_inventory.csv'
    with inventory.open(encoding='utf-8', newline='') as handle:
        entries = list(csv.DictReader(handle))
    failures = []
    checked = 0
    for entry in entries:
        path = ROOT / entry['new_path']
        if not path.is_file():
            failures.append('Missing artifact: ' + entry['new_path'])
        elif entry['preservation'] == 'unchanged':
            checked += 1
            if sha256(path) != entry['original_sha256']:
                failures.append('Artifact hash changed: ' + entry['new_path'])
    print(f'Original inventory: {len(entries)} files; {checked} unchanged-content hashes checked.')

    original = json.loads((ROOT / 'prompts/combined_examples_original.json').read_text(encoding='utf-8'))
    for profile in ('one_shot', 'few_shot'):
        split = json.loads((ROOT / f'prompts/{profile}/examples.json').read_text(encoding='utf-8'))
        if split != {criterion: examples[profile] for criterion, examples in original.items()}:
            failures.append('Demonstration values differ: ' + profile)

    comparisons = 0
    if args.reproduced_root:
        base = args.reproduced_root.resolve()
        # Compare every preserved current CSV, not only the files that happened
        # to be regenerated. Missing results must fail verification.
        expected = list((ROOT / 'outputs/parsed/normalized').glob('*.csv'))
        expected += list((ROOT / 'outputs/parsed/aggregation').glob('*.csv'))
        for rq in ('rq1', 'rq2', 'rq3'):
            expected += list((ROOT / 'results' / rq).rglob('*.csv'))
        for preserved in sorted(expected):
            relative = preserved.relative_to(ROOT)
            reproduced = base / relative
            if not reproduced.is_file():
                failures.append('Missing regenerated CSV: ' + relative.as_posix())
                continue
            if csv_contents(preserved) != csv_contents(reproduced):
                failures.append('CSV contents differ: ' + relative.as_posix())
            comparisons += 1
        print(f'Compared {comparisons} regenerated CSVs with preserved data/results (including field values and duplicate rows).')

    if failures:
        for failure in failures:
            print('FAIL:', failure)
        raise SystemExit(1)
    print('PASS: preservation and requested comparisons.')


if __name__ == '__main__':
    main()
