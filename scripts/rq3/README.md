# RQ3: reliability and high-confidence stable errors

## High-confidence, stable, but incorrect units

`analyze_high_confidence_stable_errors.py` is a new reproducibility implementation of the definition explicitly supplied by the study owner. It is not presented as recovered original analysis code.

The unit is **model × prompt_profile × project × story_id × criterion**. A unit qualifies only when:

1. Exactly five individual executions are present, with distinct configured run IDs `1`–`5`.
2. All five predictions are the same binary label: `Violation` or `No Violation`.
3. That unanimous prediction differs from the unique human binary reference label.
4. All five confidence values equal the literal string `High`.

No majority voting, pooling of prompt profiles, label conversion, confidence imputation, or replacement of missing executions is performed. `Moderate` and `Low` are valid confidence values but cannot satisfy condition 4. Blank, misspelled, case-varied or whitespace-padded labels are diagnosed rather than silently normalized.

Expected units come from configured model labels and prompt profiles, canonical story IDs, and QUS criteria. Units with zero predictions are therefore reported too. Five rows with duplicate run IDs do not constitute five valid executions. Unexpected units, missing/duplicate/nonbinary references, invalid predictions and missing/invalid confidence are explicitly excluded and recorded. Undefined derived fields and percentages with a zero denominator remain blank.

## Run independently on preserved predictions

From the repository root, using the environment described in [REPRODUCIBILITY.md](../../docs/REPRODUCIBILITY.md):

```text
python -m scripts.rq3.analyze_high_confidence_stable_errors --output-root replication_runs/rq3_high_confidence
```

The default input is `outputs/parsed/normalized/llm_predictions.csv`; the reference path comes from `config/experiment.json`. To use an independently regenerated run-level CSV, supply `--input <path>`. `--ground-truth <path>` selects an explicit reference for diagnostic comparison. Inputs must contain the required individual-run and reference columns; majority-vote schemas are rejected.

The shared path utilities keep outputs below a separate reproduction root. Without `--output-root`, the script uses `TOSEM_OUTPUT_ROOT` or `replication_runs/latest/`. It does not overwrite raw predictions, normalized data, or preserved experimental results. No extra dependency is needed.

## Generated files

All paths below are relative to the chosen output root. With the command above, they start with `replication_runs/rq3_high_confidence/`.

| File | Contents |
| --- | --- |
| `results/rq3/metrics/high_confidence_stable_incorrect_units.csv` | Every qualifying unit, identifiers, dimension, reference, unanimous prediction, run/high-confidence counts, flags and diagnostics |
| `results/rq3/metrics/high_confidence_stable_incorrect_all_units_audit.csv` | Every expected or observed unit, including complete nonqualifiers and entirely absent units |
| `results/rq3/metrics/high_confidence_stable_incorrect_excluded_units.csv` | Excluded units and explicit reasons; header-only when no exclusions exist |
| `results/rq3/metrics/high_confidence_stable_incorrect_audit_summary.json` | Stage counts, mismatch status, exclusions, observed confidence labels, extra reference keys, input paths and SHA-256 hashes |
| `results/rq3/tables/high_confidence_stable_incorrect_by_model.csv` | Counts and percentage of all qualifying units |
| `results/rq3/tables/high_confidence_stable_incorrect_by_criterion.csv` | Counts and percentage of all qualifying units |
| `results/rq3/tables/high_confidence_stable_incorrect_by_model_criterion.csv` | Counts, percentage within the model's qualifying units, and percentage of all qualifying units |
| `results/rq3/tables/high_confidence_stable_incorrect_by_prompt.csv` | Counts by prompt profile and percentage of all qualifying units |
| `results/rq3/tables/high_confidence_stable_incorrect_by_project.csv` | Counts by project and percentage of all qualifying units |

Percentages use a 0–100 scale and describe the distribution of qualifying errors, not error rates over all evaluated units. Tables include zero-count configured categories. Unit CSVs sort by model, prompt profile, project, criterion, story ID; tables sort by their grouping keys.

The console reports complete units evaluated, incomplete units, exclusions, stable units, stable incorrect units, qualifying units and comparison with the manuscript's **1,910**. `MATCH` does not override a separate data-quality failure. A mismatch or data-quality issue produces diagnostics before exit status 1; a clean match exits 0. A schema/configuration failure raises an explicit error before writing results.

On the preserved input inspected for this implementation: 21,294 complete units, 0 incomplete/excluded units, 19,200 stable units, 2,249 stable incorrect units, and **1,910 high-confidence stable incorrect units (MATCH)**. Model counts are DeepSeek V4 Pro 473, GPT-5 Mini 479, and Gemini 3.1 Pro Preview 958. These are computed verification results, not corrections to the original files or manuscript.

## Pipeline integration and tests

```text
python -m scripts.rq3.run_analysis
python -m scripts.reproduce --output-root replication_runs/check
python -m unittest scripts.rq3.test_high_confidence_stable_errors
```

The RQ3 entry point first executes the existing shared RQ1/RQ3 pipeline. Only after successful normalization/auditing does it pass the newly generated individual-run CSV to the confidence audit. The full reproduction command also uses this entry point. The RQ1 entry point alone continues to run the existing shared analyses without this additional audit.

This implementation addresses consistently incorrect, unanimously High-confidence units only. It does not add general confidence calibration, other confidence-versus-correctness/agreement analyses, qualitative sampling, or missing manuscript plotting procedures.
