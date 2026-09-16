# Reproducing the QUS-13 experiment

This project compares three LLMs under zero-shot, one-shot, and few-shot prompting against a human Gold Standard for 13 QUS criteria. AQUSA provides a rule-based baseline for five criteria.

Clone the repository and enter its root directory before running the commands below:

```text
git clone https://github.com/izabellaribeiro/TOSEM-Experiment.git
cd TOSEM-Experiment
```

If you already have a local copy, open a terminal in `TOSEM-Experiment/`, alongside this README. The repository is private, so cloning requires an authorized GitHub account.

## 1. Experimental inputs and expected scale

The execution settings are in [config/experiment.json](config/experiment.json).

| Provider | Configured model ID | Output label |
| --- | --- | --- |
| OpenAI | `gpt-5-mini` | `GPT-5-Mini` |
| Google | `gemini-3.1-pro-preview` | `Gemini-3.1-Pro-Preview` |
| DeepSeek | `deepseek-v4-pro` | `DeepSeek-V4-Pro` |

These are the identifiers used by this repository. New collection requires access to these models through the respective APIs.

| Project | Canonical stories |
| --- | ---: |
| PlanningPoker | 53 |
| BADCamp | 69 |
| Zooniverse | 60 |
| Total | 182 |

- Execution datasets: `data/canonical/*.txt`, one story per line, and matching `*_id_map.json` files. `data/source_inputs/` contains provenance inputs rather than execution datasets.
- Gold Standard: `ground_truth/gold_standard_qus13_final.csv`, containing 2,366 story–criterion units (182 × 13).
- Criteria: [config/criteria.json](config/criteria.json).
- Prompts: `prompts/system.txt`, `prompts/zero_shot.txt`, `prompts/one_shot.txt`, and `prompts/few_shot.txt`.
- Demonstrations: [config/prompt_examples.json](config/prompt_examples.json). Zero-shot uses 0 examples, one-shot uses 1, and few-shot uses 4 synthetic criterion-specific examples, balanced as 2 `Violation` and 2 `No Violation` where applicable. Experimental stories are not used as demonstrations.

The full design contains 3 models × 3 projects × 13 criteria × 3 prompt profiles × 5 runs = **1,755 logical API tasks**, producing **106,470 LLM classifications**. Each task evaluates a project's whole backlog for one criterion. Retries and failed executions can increase the actual HTTP request count. Per model, there are 585 tasks and 35,490 classifications.

The runner uses configured temperature 0 for Google and DeepSeek and omits the temperature parameter for GPT-5 Mini through `request_options.omit_temperature`.

## 2. Create the environment

Use Python **3.13.5** to match the version recorded in the supplied local environment. Create a new virtual environment on your machine; the existing `.venv-tosem/` directory is not portable. Internet access is needed for installing packages, downloading NLTK data, and making new LLM calls.

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install -r requirements.txt
python -m pip install -r vendor/aqusa-core/requirements-experiment.txt
python scripts/setup_aqusa_nltk.py
```

If PowerShell blocks activation, replace `python` in every subsequent command with `.\.venv\Scripts\python.exe`. If `py -3.13` is unavailable, install Python 3.13 first.

### Linux / macOS (Bash)

With Python 3.13 installed:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install -r requirements.txt
python -m pip install -r vendor/aqusa-core/requirements-experiment.txt
python scripts/setup_aqusa_nltk.py
```

The main requirements install `requests>=2.32,<3`. AQUSA's experiment requirements install `nltk==3.9.2` and `yattag==1.11.1`; use these instead of `requirements-original.txt`. The NLTK script downloads `punkt`, `punkt_tab`, `averaged_perceptron_tagger`, `averaged_perceptron_tagger_eng`, `wordnet`, and `omw-1.4`. Confirm that downloads succeed.

For the statistical analysis in step 8, also install:

```text
python -m pip install numpy pandas scipy
```

Dependencies are not fully pinned. Record the resolved versions with your results as described in step 9.

## 3. Validate the input data

```text
python src/validate_setup.py
```

Expected output includes:

```text
OK: 182 canonical stories, 13 QUS criteria, 2,366 Ground Truth units.
OK counts: {'PlanningPoker': 53, 'BADCamp': 69, 'Zooniverse': 60}
AQUSA-supported criteria: Well-formed, Atomic, Minimal, Unique, Uniform
```

This validates dataset and Gold Standard counts. It does not test credentials, model access, or NLTK installation.

## 4. Choose a reproduction path

**Reanalyze saved responses:** if `results/raw/` contains complete responses for the three profiles and `results/raw/AQUSA/` contains all three baseline reports, proceed to step 7. No API keys or new API calls are needed. If only the AQUSA reports are missing, run step 6 first.

**Collect new responses:** follow steps 5–9. API calls use your provider accounts and incur charges. Completed results are skipped automatically, so use a separate project copy with an empty `results/` directory for an entirely new experiment. Preserve the original results first.

Normalization, metrics, tables, and statistical analysis overwrite their corresponding derived files. Use a separate copy if you need to preserve those artifacts as well.

## 5. Configure credentials and execute the LLMs

### Set environment variables

The code reads environment variables directly and **does not automatically load `.env`**. `.env.example` lists the required variables. Set them in the terminal used to run the experiment, replacing the placeholders with your keys.

PowerShell:

```powershell
$env:OPENAI_API_KEY = "YOUR_OPENAI_KEY"
$env:GEMINI_API_KEY = "YOUR_GEMINI_KEY"
$env:DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_KEY"
```

Bash:

```bash
export OPENAI_API_KEY="YOUR_OPENAI_KEY"
export GEMINI_API_KEY="YOUR_GEMINI_KEY"
export DEEPSEEK_API_KEY="YOUR_DEEPSEEK_KEY"
```

Only the selected provider's key is needed when running one model. Keep credentials out of shared files and version control.

### Inspect prompts without calling APIs

```text
python src/run_llms.py --dry-run --model gpt-5-mini --project PlanningPoker --criterion Atomic --run 1
```

Expect three `DRY` entries, one per prompt profile. This writes `atomic.request.json` under each profile's `results/raw/<profile>/GPT-5-Mini/PlanningPoker/run_01/` directory. It needs no credentials and produces no predictions. It can overwrite existing request files, so run it in your reproduction copy.

### Check a small live execution

```text
python src/run_llms.py --model gpt-5-mini --project PlanningPoker --criterion Atomic --prompt-profile zero_shot --run 1
```

Expect `OK` for a new successful task or `SKIP` if a completed result is present. Repeat with `--model gemini-3.1-pro-preview` and `--model deepseek-v4-pro` to check the other providers.

### Execute the full experiment

```text
python src/run_llms.py
```

Alternatively, run one profile at a time:

```text
python src/run_llms.py --prompt-profile zero_shot
python src/run_llms.py --prompt-profile one_shot
python src/run_llms.py --prompt-profile few_shot
```

Combine filters to execute a subset: `--provider` (`openai`, `google`, `deepseek`), `--model`, `--project` (`PlanningPoker`, `BADCamp`, `Zooniverse`), `--criterion`, `--prompt-profile`, and `--run` (use 1–5 for this design). Criterion names must match the configuration exactly; quote names containing spaces, for example `--criterion "Conceptually sound"`.

### Check failures and resume

Artifacts are stored under:

```text
results/raw/<prompt_profile>/<model_label>/<project>/run_01/
    <criterion_slug>.request.json
    <criterion_slug>.response.json
    <criterion_slug>.parsed.json
    <criterion_slug>.error.txt
```

The error file is written on failure and removed after a successful retry. Request/response files may be absent when the API call itself fails. The runner catches task errors and continues, so process completion alone does not prove experiment completion. Inspect `ERROR` messages and `.error.txt` files, resolve their causes, and rerun the same command.

Resume checks the parsed file's project, criterion, run, profile, and evaluation count before skipping it. It does not compare prompt, input, or configuration hashes. Use a separate experiment copy if those inputs change.

## 6. Execute the AQUSA baseline

After installing AQUSA dependencies and NLTK resources in step 2:

```text
python src/run_aqusa.py
```

This runs the bundled `vendor/aqusa-core/` implementation with canonical datasets and writes:

```text
results/raw/AQUSA/PlanningPoker.txt
results/raw/AQUSA/BADCamp.txt
results/raw/AQUSA/Zooniverse.txt
```

To execute one project, use `python src/run_aqusa.py --project PlanningPoker`. AQUSA requires no API credentials. Direct LLM–AQUSA comparison uses **Well-formed, Atomic, Minimal, Unique, and Uniform**. For these criteria, normalization treats an alert as `Violation` and the absence of an alert as `No Violation`.

## 7. Normalize, audit, and calculate metrics

Run each command in order and check its output before continuing:

```text
python src/normalize_llm.py
python src/normalize_aqusa.py
python src/audit_quantitative.py
python src/metrics.py
python src/build_quantitative_tables.py
```

Verify the following for the complete configuration:

| Check | Expected result |
| --- | --- |
| LLM normalization | 106,470 rows in `results/normalized/llm_predictions.csv` |
| AQUSA normalization | 910 rows (182 × 5) in `results/normalized/aqusa_predictions.csv` |
| Quantitative audit | `AUDIT RESULT: PASS`, no duplicate keys, all five runs represented |
| Audit report | `results/audit/audit_summary.json` |
| Metrics | CSV files in `results/metrics/` |
| Summary tables | Files in `results/tables/` |

Resolve audit failures before reporting full-experiment results. Partial runs do not satisfy the full audit. The audit checks normalized LLM coverage, not AQUSA reports; verify the three reports and 910 baseline rows separately. The AQUSA normalizer prints `Missing` and continues when a report is absent.

Metrics include per-run effectiveness, means and standard deviations, cross-run variability, majority-vote metrics, and false-positive/false-negative details. `Violation` is the positive class; Gold Standard labels `Uncertain` and `Insufficient Context` are excluded from primary binary metrics. See [docs/metrics_dictionary.md](docs/metrics_dictionary.md).

## 8. Reproduce the prompting statistics

After step 7 and installation of `numpy`, `pandas`, and `scipy`:

```text
python scripts/analyze_prompting_statistics.py
```

The default metric is F1. The script reads `results/metrics/effectiveness_by_run.csv` and writes to `results/statistical_analysis/`. It averages repeated runs within matched model–project–criterion–prompt units, excludes partitions without positive Gold Standard instances, and compares the three prompts using Friedman and pairwise Wilcoxon tests with Holm correction and effect sizes. AQUSA is excluded from this prompting comparison.

To analyze MCC while keeping the F1 outputs:

```text
python scripts/analyze_prompting_statistics.py --metric MCC --output-dir results/statistical_analysis_mcc
```

Inspect the reported matched-unit and run counts before interpreting the statistical results.

## 9. Preserve reproduction metadata

Record the resolved dependencies and Python version:

```text
python -m pip freeze > results/requirements-resolved.txt
python --version > results/python-version.txt
```

Preserve the source snapshot, `config/`, `prompts/`, `data/canonical/`, `ground_truth/gold_standard_qus13_final.csv`, raw responses, and derived outputs. New remote-model executions can produce different predictions; reanalysis of saved responses is the path for checking the existing quantitative results.

**Current manifest limitation:** `src/create_manifest.py` references `ground_truth/gold_standard_qus13.csv`, which is absent; the configured file is `gold_standard_qus13_final.csv`. Consequently, the manifest script currently fails. `run_all.sh` invokes that script at its last step and does not include statistical analysis. Use the explicit steps above until the manifest path is corrected. The manifest script also does not hash every dataset and source file.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Wrong Python version or missing module | Check `python --version`; use the virtual environment interpreter for installation and execution. |
| `KeyError` naming an API key | Set the variable in the current terminal; saving `.env` alone is insufficient. |
| API authentication, model-access, or quota error | Inspect the task's `.error.txt`, correct the account/key/access issue, and rerun the subset. |
| NLTK `LookupError` | Rerun `python scripts/setup_aqusa_nltk.py` with the same interpreter and user account as AQUSA; confirm downloads succeed. |
| No matching LLM tasks | Check exact model, project, and criterion spelling. |
| Audit reports missing rows | Finish or retry missing tasks, then rerun normalization and the audit. |
| Old results are reused | Review resume behavior in step 5; use an independent copy for changed inputs. |

Further details: [experimental design](docs/experiment_design.md), [prompt strategy](docs/prompt_strategy.md), [dataset consistency](docs/dataset_consistency.md), and [AQUSA integration](docs/aqusa_integration.md).
