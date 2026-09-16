"""Artifact locations; regenerated files stay separate from preserved results."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def output_root():
    path = Path(os.environ.get('TOSEM_OUTPUT_ROOT', ROOT / 'replication_runs/latest')).resolve()
    # Never permit regeneration to overwrite the preserved publication artifacts.
    if path == ROOT or any(path == ROOT / name or ROOT / name in path.parents
                           for name in ('data', 'outputs', 'results', 'docs', 'prompts', 'vendor')):
        raise ValueError('Use a separate output directory, such as replication_runs/latest.')
    return path


def generated_path(relative):
    return output_root() / relative


def metric_relative(name):
    if name == 'majority_vote_predictions.csv':
        return 'outputs/parsed/aggregation/' + name
    rq = 'rq3' if name in {'majority_vote_metrics.csv', 'unit_detection_frequency.csv', 'variability.csv'} else 'rq1'
    return f'results/{rq}/metrics/{name}'


def metric_path(name):
    return generated_path(metric_relative(name))


def table_relative(name):
    rq = 'rq2' if name.startswith(('05_', '09_')) else 'rq3' if name.startswith(('06_', '07_')) else 'rq1'
    return f'results/{rq}/tables/{name}'


def table_path(name):
    return generated_path(table_relative(name))
