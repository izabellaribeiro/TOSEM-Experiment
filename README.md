# TOSEM replication package: Beyond Accuracy

Replication artifacts for **Beyond Accuracy: A Multidimensional Evaluation of LLMs for User Story Quality Assessment**, by Izabella R. S. Silva and coauthors. The supplied 2026 manuscript evaluates predictive effectiveness, prompting, repeated-run reliability, and rationale quality across the 13 Quality User Story (QUS) criteria.

This package contains preserved experimental inputs, API outputs, analysis code, quantitative results, and human qualitative coding workbooks. **Quantitative reanalysis is executable; confidence analysis and qualitative sample selection are not fully reproducible from the supplied scripts.** See [reproducibility instructions](docs/REPRODUCIBILITY.md), [artifact traceability](docs/TRACEABILITY.md), and [manual-review items](docs/MANUAL_REVIEW.md).

## Study overview

| Factor | Preserved configuration |
| --- | --- |
| Projects | PlanningPoker: 53 stories; BADCamp: 69; Zooniverse (Zooniverse/MICO in the article): 60 |
| Assessment units | 182 stories × 13 QUS criteria = 2,366 story–criterion pairs |
| Models | GPT-5 Mini (`gpt-5-mini`), Gemini 3.1 Pro Preview (`gemini-3.1-pro-preview`), DeepSeek V4 Pro (`deepseek-v4-pro`) |
| Prompting | Zero-shot: 0 demonstrations; one-shot: 1; few-shot: 4 |
| Repetitions | 5 runs per model–project–criterion–prompt condition |
| Collection size | 1,755 completed logical API tasks; 106,470 parsed LLM classifications |
| Baseline | AQUSA: Well-formed, Atomic, Minimal, Unique, Uniform; 910 normalized classifications |

Each API task evaluates one complete project backlog for one criterion. Demonstrations are synthetic and external to the three evaluated datasets. Few-shot demonstrations use two violations and two non-violations where applicable. The runner uses temperature 0 for Gemini and DeepSeek and omits temperature for GPT-5 Mini, as configured in [config/experiment.json](config/experiment.json). API retries can increase the actual HTTP request count beyond the logical task count.

## Human reference and qualitative coding

The final [Gold Standard](data/ground_truth/gold_standard_qus13_final.csv) contains **303 `Violation` and 2,063 `No Violation` labels**. The supplied manuscript (§3.2) reports two pilot rounds with three experts, a second-pilot Fleiss' kappa of 0.81, and project-wise annotation under the calibrated protocol. It states that all **251 initially `Uncertain` cases were reviewed by the three experts and resolved through human consensus before automated outputs were examined**.

The final CSV supports the resulting binary counts. The individual pilot annotations and case-level records of that 251-case adjudication are not present, so that historical process cannot be independently reconstructed from this package. Historical documentation describing 251 excluded cases is retained as an earlier state, not the current reference policy. See [ground-truth provenance](data/ground_truth/README.md).

RQ4 is a separate human evaluation of **30 LLM rationales**, using Rationale Correctness (RC) and Evidence Support (ES). The two coder workbooks, adjudication workbook, and final workbook are preserved unchanged. They are not records of the 251-case Gold Standard adjudication.

## Repository structure

```text
TOSEM-Experiment/
├── README.md
├── requirements.txt
├── config/                      # Execution settings and QUS definitions
├── data/
│   ├── raw/                     # Original supplied input datasets
│   ├── ground_truth/            # Final human reference labels
│   ├── processed/               # Canonical execution datasets and ID maps
│   └── qualitative_sample/      # Coder and adjudication workbooks
├── prompts/
│   ├── system.txt               # Shared system instructions
│   ├── zero_shot/               # Frozen template
│   ├── one_shot/                # Frozen template and demonstration values
│   └── few_shot/                # Frozen template and demonstration values
├── outputs/
│   ├── raw/                    # Requests, API responses, and AQUSA reports
│   └── parsed/                 # Parsed JSONs, normalized CSVs, aggregation
├── scripts/
│   ├── rq1/                    # Effectiveness entry point
│   ├── rq2/                    # Existing prompting statistics
│   ├── rq3/                    # Stability/aggregation entry point
│   ├── rq4/                    # Manual workflow and missing-script notice
│   ├── execution/              # Model collection and normalization
│   ├── shared/                 # Existing shared calculations and utilities
│   └── archive/                # Historical mock utility, not research evidence
├── results/
│   ├── rq1/                    # Effectiveness and AQUSA comparisons
│   ├── rq2/                    # Prompting tables and inferential statistics
│   ├── rq3/                    # Stability and majority-vote metrics
│   ├── rq4/                    # Final adjudicated qualitative workbook
│   └── archive/                # Earlier single-prompt artifacts, manual review
├── docs/
│   ├── TRACEABILITY.md
│   ├── REPRODUCIBILITY.md
│   ├── MANUAL_REVIEW.md
│   ├── provenance/             # File inventory, hashes, original audit/manifest
│   └── history/                # Original documentation retained unchanged
└── vendor/aqusa-core/           # Preserved third-party baseline and license
```

The raw and parsed output trees each have an `archive/previous_single_prompt/` subtree. Archived files never enter current normalization. `replication_runs/` is created locally for regenerated artifacts and ignored by Git.

## Research questions and entry points

| RQ / article results section | Available analysis | Main location |
| --- | --- | --- |
| RQ1 / §4.1 | Effectiveness by model, criterion, dimension, project; supported-five AQUSA comparison | `scripts/rq1/`, `results/rq1/` |
| RQ2 / §4.2 | Prompt summaries, Friedman test, pairwise Wilcoxon tests, Holm correction, effect sizes | `scripts/rq2/`, `results/rq2/` |
| RQ3 / §4.3 | Jaccard, unanimity/flip rates, Fleiss' kappa, detection frequencies, majority voting | `scripts/rq3/`, `results/rq3/` |
| RQ3 / §4.3 | Confidence versus correctness/agreement | Confidence fields exist in parsed outputs; dedicated analysis script is missing |
| RQ4 / §4.4 | RC/ES coding and adjudicated summaries | `data/qualitative_sample/`, `results/rq4/`; manual inspection |

The RQ1 and RQ3 entry points call the same preserved metrics implementation, which calculates both sets of outputs and descriptive RQ2 tables. These entry points are new orchestration only, not newly invented analyses.

## Quick start: reanalyze the saved experiment

Clone the repository using an account with access and enter its root:

```text
git clone https://github.com/izabellaribeiro/TOSEM-Experiment.git
cd TOSEM-Experiment
```

Use Python 3.13.5 to match the preserved execution manifest. On Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m scripts.reproduce --output-root replication_runs/check
```

On Linux/macOS with Python 3.13 installed:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m scripts.reproduce --output-root replication_runs/check
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` instead of `python`. Existing virtual environments copied from another machine or directory should be recreated.

This command makes **no API calls**. It regenerates normalized outputs, audits LLM coverage, calculates the available RQ1/RQ3 analyses and RQ2 tables/statistics, and records the current reproduction environment. It writes to `replication_runs/check/`, preserving `outputs/` and `results/`. Expected counts are 106,470 LLM rows and 910 AQUSA rows, with `AUDIT RESULT: PASS`.

To check preservation and compare regenerated CSV contents:

```text
python -m scripts.verify_package --reproduced-root replication_runs/check
```

For per-RQ instructions, input/output paths, new model collection, NLTK installation, and the manual RQ4 workflow, read [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md). `bash run_all.sh` is a convenience wrapper for saved-output reanalysis.

## Dependencies and reproducibility limits

[requirements.txt](requirements.txt) lists only dependencies used by existing execution and analysis code: `requests`, `nltk`, `yattag`, `numpy`, `pandas`, and `scipy`. AQUSA's experiment pins are retained. Other versions were not fully pinned in the source package; the reproduction manifest records installed versions without presenting them as original execution metadata. Excel-compatible software is needed to inspect the preserved `.xlsx`/`.xlsm` workbooks; macros are not required for the documented inspection workflow.

The supplied scripts do not recreate the 30-case sampling process, confidence-analysis tables, qualitative agreement calculations, or every article-level table/figure. No missing seed, sampling algorithm, result, or methodological decision has been invented. See [MANUAL_REVIEW.md](docs/MANUAL_REVIEW.md).

## Citation

The supplied manuscript contains placeholder DOI and publication fields. Until authoritative publication metadata is available, cite it as a manuscript:

> Silva, Izabella R. S.; Dantas Filho, Emanuel; Andrade, Lucas Santos; Sousa Neto, Ademar; Perkusich, Mirko; Albuquerque, Danyllo Wagner; Gorgônio, Kyller Costa; and Perkusich, Angelo. 2026. *Beyond Accuracy: A Multidimensional Evaluation of LLMs for User Story Quality Assessment*. Manuscript supplied with this replication-package organization request.

For the repository, cite *TOSEM-Experiment: replication artifacts for Beyond Accuracy*, [GitHub repository](https://github.com/izabellaribeiro/TOSEM-Experiment), and the exact commit used (`git rev-parse HEAD`). No repository DOI or release version has been supplied. The organization branch is `replication-package-organization`.
