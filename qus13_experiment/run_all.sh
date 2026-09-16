#!/usr/bin/env bash
set -euo pipefail
python src/validate_setup.py
python src/run_llms.py
python src/run_aqusa.py
python src/normalize_llm.py
python src/normalize_aqusa.py
python src/metrics.py
python src/audit_quantitative.py
python src/build_quantitative_tables.py
python src/create_manifest.py
