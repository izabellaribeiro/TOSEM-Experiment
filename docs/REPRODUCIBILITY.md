# Reproducibility instructions

Run all commands from the repository root. Python modules are invoked with `python -m ...` so shared imports work after reorganization. These steps reproduce the supplied analyses; they do not recreate missing research procedures.

## 1. Install the environment

Use Python 3.13.5 to match the original execution manifest. Create a fresh environment rather than reusing a relocated environment.

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If activation is blocked on Windows, replace `python` with `.\.venv\Scripts\python.exe`. The requirements list the six packages directly imported by execution/analysis code. `numpy`, `pandas`, and `scipy` serve RQ2; `requests` serves model APIs; `nltk` and `yattag` serve AQUSA. Exact historical versions are not fully available. PDF extraction used during package inspection is not a runtime dependency and is not in requirements.

Saved-output reanalysis needs no API credentials and no NLTK downloads. To execute AQUSA itself, also run:

```text
python scripts/setup_aqusa_nltk.py
```

Confirm downloads succeed for `punkt`, `punkt_tab`, `averaged_perceptron_tagger`, `averaged_perceptron_tagger_eng`, `wordnet`, and `omw-1.4`. Use the same interpreter and user account for setup and execution. The vendor's `requirements-original.txt` is historical; use the experiment-specific versions already included in root requirements.

## 2. Validate preserved inputs

```text
python -m scripts.shared.validate_setup
python -m scripts.verify_package
```

The first command checks 182 canonical stories, 13 criteria and 2,366 Gold Standard units. The package check verifies the preservation inventory and split demonstration values. It does not prove the historical human annotation process or model access.

The current reference contains 303 violations and 2,063 non-violations. The generic metric code retains the policy to exclude `Uncertain` and `Insufficient Context`; the supplied final reference has neither label. Do not substitute the historical counts in `docs/history/ground_truth_quality_check.md` for the final labels.

## 3. Reproduce all available quantitative analyses

```text
python -m scripts.reproduce --output-root replication_runs/check
python -m scripts.verify_package --reproduced-root replication_runs/check
```

The first command normalizes the saved current parsed JSONs and AQUSA reports, audits coverage, calculates the existing shared RQ1/RQ3 metrics and RQ1–RQ3 descriptive tables, runs the high-confidence stable-error audit and RQ2 statistical analysis, and records the current environment. It does not call any model API or invent missing RQ4 procedures.

All regenerated artifacts are written below `replication_runs/check/`, not over the preserved files. Using the same output root again overwrites only that reproduction's generated files; choose a different output root to retain separate checks. The default root is `replication_runs/latest/`. The environment variable `TOSEM_OUTPUT_ROOT` selects an alternative root for individual module commands; the all-analysis command sets it for its subprocesses.

The package verification compares CSV rows without relying on file ordering. This permits row-order and newline differences without accepting changed field values. [VALIDATION.md](VALIDATION.md) records the checks performed during organization.

## 4. RQ1: effectiveness and AQUSA comparison

```text
python -m scripts.rq1.run_analysis
```

Inputs:

- `data/ground_truth/gold_standard_qus13_final.csv` and `config/criteria.json`;
- `outputs/parsed/{zero_shot,one_shot,few_shot}/<model>/<project>/run_XX/*.parsed.json`;
- all three reports in `outputs/raw/AQUSA/`.

Outputs below the selected output root:

- `outputs/parsed/normalized/llm_predictions.csv`: 106,470 rows;
- `outputs/parsed/normalized/aqusa_predictions.csv`: 910 rows;
- `audit/audit_summary.json`: expected `PASS`;
- `results/rq1/metrics/`: confusion counts, effectiveness at six aggregation levels, supported-five AQUSA comparison, error details, exclusion diagnostics, and run means/standard deviations;
- `results/rq1/tables/`: model, criterion, dimension, project, and supported-five summaries.

The shared implementation also writes RQ3 metrics, aggregation predictions, and descriptive RQ2/RQ3 tables. AQUSA is evaluated only on Well-formed, Atomic, Minimal, Unique, and Uniform. No AQUSA alert maps to `No Violation` for these criteria.

The LLM audit checks row counts, model/profile sets, duplicate prediction keys, and run coverage. It does not audit AQUSA completeness. Missing AQUSA reports are reported by the normalizer; check all three input reports and the expected 910 output rows before interpreting baseline comparisons. Do not interpret partial LLM runs as a full experiment.

## 5. RQ2: prompting analyses

Run RQ1 first in the same output root, then:

```text
python -m scripts.rq2.analyze_prompting_statistics
```

By default this reads `<output-root>/results/rq1/metrics/effectiveness_by_run.csv` and writes `<output-root>/results/rq2/statistical_analysis/`. To analyze preserved metrics directly while keeping generated files separate:

```text
python -m scripts.rq2.analyze_prompting_statistics --input results/rq1/metrics/effectiveness_by_run.csv --output-dir replication_runs/prompting/results/rq2/statistical_analysis
```

The existing script selects LLM `project_criterion` rows, excludes partitions with no positive reference cases, averages repeated runs within each model–project–criterion–prompt condition, and retains matched units with all three prompts. It computes Friedman statistics, Kendall's W, pairwise two-sided Wilcoxon tests, Holm-adjusted p-values, and matched-pairs rank-biserial correlations. It does not treat the five runs as independent inferential units.

The default metric is F1. Five CSVs contain input audits, condition means, matched units, omnibus results, and pairwise results. Inspect the input audit and matched-unit counts. For MCC, specify a separate directory to preserve F1 output:

```text
python -m scripts.rq2.analyze_prompting_statistics --input results/rq1/metrics/effectiveness_by_run.csv --metric MCC --output-dir replication_runs/prompting_mcc/results/rq2/statistical_analysis
```

The existing CLI accepts an explicit output directory; do not point it at preserved `results/rq2/`.

## 6. RQ3: stability, confidence, and aggregation

```text
python -m scripts.rq3.run_analysis
```

This first calls the shared RQ1 implementation, then runs the high-confidence stable-error audit on the regenerated run-level CSV. If RQ1 already ran, its stability/aggregation outputs exist; the new confidence audit can be invoked separately as documented below.

Inspect:

- `results/rq3/metrics/variability.csv`: pairwise Jaccard, unanimous-unit rate, flip rate, Fleiss' kappa, available runs;
- `results/rq3/metrics/unit_detection_frequency.csv`: per-unit violation frequency and flip indicator;
- `outputs/parsed/aggregation/majority_vote_predictions.csv`: predictions, vote counts, runs available;
- `results/rq3/metrics/majority_vote_metrics.csv` and `results/rq3/tables/`: supported aggregation/stability summaries.

The original metrics implementation is preserved: in particular, majority voting is computed for units with at least three available predictions. The full reproduction is required to pass the five-run audit before these results are used.

**High-confidence stable-error audit:** `python -m scripts.rq3.analyze_high_confidence_stable_errors --output-root replication_runs/rq3_high_confidence` analyzes preserved individual-run predictions using the study owner's explicit definition: five distinct runs, unanimous incorrect binary prediction, and literal `High` confidence in every run. It verifies the manuscript count of 1,910 without forcing agreement and writes exclusions and a full unit audit. See [RQ3 instructions](../scripts/rq3/README.md) for outputs and failure statuses. Broader confidence-versus-correctness/agreement analyses remain a gap; this is a newly implemented reproducibility analysis, not recovered original code.

## 7. RQ4: qualitative sample and human analysis

The preserved artifacts permit inspection of the selected cases and final judgments, not regeneration of the original sample. Open the workbooks in an Excel-compatible application without enabling macros:

1. `data/qualitative_sample/qualitative_evaluation_coder1.xlsx` and `qualitative_evaluation_coder2.xlsx`: read `Instructions` and `Codebook`; inspect the 30 identified cases in `Evaluation` and their backlog context in `Backlog Reference`. Ignore formatting-only rows with no Case ID.
2. Compare the two coders' recorded RC and ES labels by Case ID. Preserve the original judgments; do not recode or replace them during reproduction.
3. `data/qualitative_sample/adjudication.xlsm`: inspect `Adjudication`, `Summary`, and `Instructions` for recorded disagreements and decisions. The workbook may contain macros, but none is executed by this package.
4. `results/rq4/final_adjudicated.xlsx`: inspect `Final Coding`, `Adjudicated Cases`, `Final Summary`, and `Method Note`. The recorded final sample has 30 cases: 8 TP, 8 TN, 7 FP and 7 FN. RC2/RC1/RC0 counts are 14/11/5; ES2/ES1/ES0 counts are 17/10/3. These are existing workbook values, not newly generated research results.

**Author-clarified sampling procedure:** the original sample was selected manually using stratified, coverage-oriented selection. Individual run-level candidates were organized into TP, TN, FP and FN, inspected manually case by case, and selected for approximate quadrant balance and diversity across model, prompting strategy, QUS criterion and project. The sample is exploratory, not intended for population-level statistical representativeness. **No random sampling or random seed was used**; a seed is not missing metadata.

The existing case provenance can now be recovered reproducibly with:

```text
python -m scripts.rq4.build_sampling_manifest
```

This reads the fixed final/coder workbooks and normalized predictions and writes `data/qualitative_sample/sampling_manifest.csv`, `sampling_candidate_matches.csv`, and `sampling_manifest_audit.json`. It does not select cases, alter human coding, or replay manual judgments. The manifest records all 30 cases, the author-confirmed method `manual_stratified_coverage_selection`, and supported source fields. There are 20 unique run matches; Q10–Q18 and Q29 remain ambiguous, with blank run values and all alternatives preserved separately. All 30 cases have supported model and prompt values. The observed sample has 8 TP, 8 TN, 7 FP, 7 FN, and 10 cases per model, prompt and project. The matching inputs, source hashes and criterion coverage are documented in the audit JSON.

**Remaining gaps:** a unique source execution cannot be assigned to the ten ambiguous cases without additional original records. The final workbook records agreement statistics and summaries, but their calculation/export script is not present. The steps above verify recorded artifacts and recover supported provenance; they do not constitute executable reproduction of manual selection judgments, coder independence, agreement calculation, or adjudication history. Request the unresolved source keys and the original analysis script or documented workbook formulas/export procedure from the authors.

## 8. Collect new model responses, if needed

Use a separate project copy with empty `outputs/raw/` and `outputs/parsed/` trees when collecting an entirely new experiment; preserve the supplied outputs first. Do not delete the only copy of the experimental evidence. New remote model responses need not equal the preserved responses.

The runner reads environment variables directly; it does not load `.env` automatically. Set keys in the same terminal, replacing placeholders:

```powershell
$env:OPENAI_API_KEY = "YOUR_OPENAI_KEY"
$env:GEMINI_API_KEY = "YOUR_GEMINI_KEY"
$env:DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_KEY"
```

For Bash:

```bash
export OPENAI_API_KEY="YOUR_OPENAI_KEY"
export GEMINI_API_KEY="YOUR_GEMINI_KEY"
export DEEPSEEK_API_KEY="YOUR_DEEPSEEK_KEY"
```

Only the selected provider's key is required for a subset. Real calls incur provider charges. Keep credentials and error logs local and ignored.

Inspect rendered requests without API calls in the separate copy:

```text
python -m scripts.execution.run_llms --dry-run --model gpt-5-mini --project PlanningPoker --criterion Atomic --run 1
```

Expect three `DRY` messages. A dry run writes request artifacts and can overwrite existing request files, so do not run it over preserved evidence. A small live task is:

```text
python -m scripts.execution.run_llms --model gpt-5-mini --project PlanningPoker --criterion Atomic --prompt-profile zero_shot --run 1
```

Run the full collection and AQUSA baseline:

```text
python -m scripts.execution.run_llms
python -m scripts.execution.run_aqusa
```

Use `--model`, `--provider`, `--project`, `--criterion`, `--prompt-profile`, and `--run` to select LLM tasks. Values must match the configuration exactly; quote criterion names with spaces. Use runs 1–5 for this design. AQUSA supports `--project`.

The runner writes requests/responses to `outputs/raw/` and validated classifications to the matching `outputs/parsed/` tree. It catches task errors and continues; inspect `ERROR` messages and local `.error.txt` files, fix the cause, and rerun the same selection. The skip check uses project, criterion, run, profile, and evaluation count, not content hashes. Changed prompts/configurations require an independent output collection.

After collection, run the saved-output reproduction steps. The normalization module reads the three current prompt subtrees only and excludes archives.

## 9. Record the environment and provenance

The all-analysis command generates `<output-root>/reproduction_manifest.json`. For individual stages:

```text
python -m scripts.shared.create_manifest
```

This records the current interpreter, platform, installed dependency versions, configuration, and source/input hashes. It does not replace or repair the original execution manifest. The original manifest's stale Gold Standard path and other limitations remain documented in [MANUAL_REVIEW.md](MANUAL_REVIEW.md).

Retain the exact Git revision, regenerated artifacts, dependency versions, and any local execution logs. Raw responses may contain provider-side timestamps and metadata but no stronger determinism guarantee is implied.
