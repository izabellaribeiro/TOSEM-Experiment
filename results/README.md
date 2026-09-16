# Results directory

This directory is intentionally shipped without experimental model outputs.

- `raw/`: immutable API/AQUSA requests and responses organized by model/project/run/criterion.
- `normalized/`: normalized prediction tables.
- `metrics/`: effectiveness, FP/FN, variability, and majority-vote tables.
- `experiment_manifest.json`: hashes and execution environment metadata.

Do not overwrite a completed run. Archive the whole `results/` directory with a run identifier/date before starting a new experiment.
