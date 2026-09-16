"""RQ1 entry point for the existing shared RQ1/RQ3 calculations and tables.

The original metrics implementation also produces stability and majority-vote
outputs for RQ3 and descriptive prompting tables for RQ2. No new estimator is
introduced by this orchestration entry point.
"""
from scripts.execution.normalize_llm import main as normalize_llm
from scripts.execution.normalize_aqusa import main as normalize_aqusa
from scripts.shared.audit_quantitative import main as audit
from scripts.shared.metrics import main as metrics
from scripts.shared.build_quantitative_tables import main as tables


def main():
    normalize_llm()
    normalize_aqusa()
    audit()
    metrics()
    tables()


if __name__ == '__main__':
    main()
