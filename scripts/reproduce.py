"""Reanalyze preserved outputs without making model API calls."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, default=ROOT / 'replication_runs/latest')
    args = parser.parse_args()
    os.environ['TOSEM_OUTPUT_ROOT'] = str(args.output_root.resolve())
    from scripts.shared.paths import output_root
    output_root()  # Validate before any writes.
    for module in ('scripts.shared.validate_setup', 'scripts.rq1.run_analysis',
                   'scripts.rq2.analyze_prompting_statistics', 'scripts.shared.create_manifest'):
        subprocess.run([sys.executable, '-m', module], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
