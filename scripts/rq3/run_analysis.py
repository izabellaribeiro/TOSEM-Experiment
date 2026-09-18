"""Run the existing shared pipeline for stability and majority voting.

This also regenerates RQ1 metrics and descriptive RQ2 tables, then audits
high-confidence stable incorrect units using the regenerated run-level CSV.
"""
from scripts.rq1.run_analysis import main as shared_pipeline
from scripts.rq3.analyze_high_confidence_stable_errors import run_analysis
from scripts.shared.paths import generated_path


def main():
    shared_pipeline()
    summary = run_analysis(generated_path('outputs/parsed/normalized/llm_predictions.csv'))
    if summary['status'] != 'MATCH' or summary['data_quality_status'] != 'PASS':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
