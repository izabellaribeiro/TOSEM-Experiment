"""Run the existing shared pipeline for stability and majority voting.

This also regenerates RQ1 metrics and descriptive RQ2 tables. The source
repository contains no dedicated confidence-analysis implementation.
"""
from scripts.rq1.run_analysis import main

if __name__ == '__main__':
    main()
