# Artifact traceability

RQ numbering follows §3.1 of the supplied manuscript: RQ1 effectiveness, RQ2 prompting, RQ3 reliability, RQ4 rationale quality. The seven proposed RQs in `history/experiment_design.md` are historical and are not the current mapping.

The machine-readable [artifact inventory](provenance/artifact_inventory.csv) maps **every originally tracked file** from its preorganization path to its current path, with its original SHA-256, scope, and preservation status. The source revision is `336deaf22fc56b6d5aabcd7d17d7f76e98e9b7f5`. Original numerical results, raw and parsed outputs, datasets, prompts, and workbooks are preserved; path/configuration/code changes are explicitly identified in the inventory. [Duplicate groups](provenance/duplicate_files.csv) are reported, not deleted.

## Study-stage mapping

| Stage / article section | Input artifact | Processing script or recorded process | Preserved output / result | Evidence limits |
| --- | --- | --- | --- | --- |
| Context / §3.2 | `data/raw/g13-planningpoker-uploaded.txt`, `g21-badcamp-uploaded.txt`, `g28-zooniverse-uploaded.txt` | Canonical export described in historical dataset documentation | `data/processed/*.txt`, `*_id_map.json` | Export script not supplied; canonical files are distinct from uploaded originals |
| Human reference / §3.2 | Pilot and project annotation records | Three-expert protocol calibration and human adjudication, as reported in manuscript | `data/ground_truth/gold_standard_qus13_final.csv` | Final labels available; pilot records and 251-case consensus audit trail absent |
| Assessment / §3.3 | Canonical datasets, config, per-profile prompts/examples | `python -m scripts.execution.run_llms` | `outputs/raw/<profile>/<model>/<project>/run_XX/*.request.json`, `*.response.json`; matching `outputs/parsed/.../*.parsed.json` | Request/response and parsed JSONs preserved byte-for-byte |
| Baseline / §3.4 | Canonical datasets; bundled AQUSA | `python -m scripts.execution.run_aqusa` | `outputs/raw/AQUSA/{PlanningPoker,BADCamp,Zooniverse}.txt` | Five supported criteria only; vendor code unchanged |
| Normalization / §3.4 | Current parsed JSONs and AQUSA reports | `scripts.execution.normalize_llm`, `scripts.execution.normalize_aqusa` | `outputs/parsed/normalized/{llm,aqusa}_predictions.csv` | Reanalysis writes separate copies under the output root |
| Coverage audit / §3.3 | Normalized LLM predictions and configuration | `scripts.shared.audit_quantitative` | Original: `docs/provenance/execution_audit/audit_summary.json`; regenerated: `<output-root>/audit/audit_summary.json` | LLM counts, profiles, model set, duplicate keys and run coverage; not a full AQUSA or methodological audit |

## RQ-to-analysis mapping

Paths in the result column refer to preserved artifacts. Reproduction writes the same relative paths below a separate output root, default `replication_runs/latest/`.

| Research question / article section | Input artifact | Processing script / entry point | Preserved result artifact |
| --- | --- | --- | --- |
| RQ1 / §4.1 effectiveness | Final Gold Standard; normalized LLM/AQUSA outputs; criteria definitions | `scripts/rq1/run_analysis.py` → `scripts/shared/metrics.py`, `build_quantitative_tables.py` | `results/rq1/metrics/effectiveness_by_run.csv`, `run_summary_mean_sd.csv`; tables `01_`–`04_` |
| RQ1 / §4.1 supported-five AQUSA comparison | Same inputs, restricted to five supported criteria | Existing shared metrics and table builder | `results/rq1/metrics/aqusa_supported5_by_run.csv`, `results/rq1/tables/08_aqusa_supported5_by_prompt_model_project_run.csv` |
| RQ1 diagnostics; RQ4 candidate context | Reference labels joined to predictions | Existing shared metrics | `results/rq1/metrics/error_details_fp_fn.csv`, `excluded_ground_truth_units.csv`; these are not the RQ4 sample selector |
| RQ2 / §4.2 descriptive effects | RQ1 per-run effectiveness | Existing shared table builder | `results/rq2/tables/05_prompt_strategy_summary.csv`, `09_prompt_ranking_within_model.csv` |
| RQ2 / §4.2 inference | `results/rq1/metrics/effectiveness_by_run.csv`, `project_criterion` rows | `scripts/rq2/analyze_prompting_statistics.py` | `results/rq2/statistical_analysis/prompting_{condition_means,input_audit,matched_units,friedman,pairwise_wilcoxon}_F1.csv` |
| RQ3 / §4.3 stability | LLM decisions across five runs and final reference | `scripts/rq3/run_analysis.py` → existing shared metrics/table builder | `results/rq3/metrics/variability.csv`, `unit_detection_frequency.csv`; table `07_variability_raw_by_prompt_model_criterion_project.csv` |
| RQ3 / §4.3 aggregation | Same inputs | Existing shared majority-vote implementation | `outputs/parsed/aggregation/majority_vote_predictions.csv`; `results/rq3/metrics/majority_vote_metrics.csv`; table `06_majority_vote_by_prompt_model_project.csv` |
| RQ3 / §4.3 confidence | `confidence` fields in parsed JSONs/normalized predictions, decisions and reference labels | **No dedicated script supplied** | **No dedicated confidence result artifacts supplied**; article-level figures require author clarification |
| RQ4 / §3.5, §4.4 sample | Thirty run-level outputs embedded in the coding workbooks | **No sample-selection script, seed, or full case-to-run key supplied** | `data/qualitative_sample/qualitative_evaluation_coder{1,2}.xlsx`, `Evaluation` sheets |
| RQ4 / §3.5, §4.4 coding and rubric | Sampled text, QUS definitions, backlog reference | Human coding; workbook `Instructions` and `Codebook` sheets | Original coder workbooks; no automated replacement of human judgments |
| RQ4 / §4.4 adjudication and summaries | Coder RC/ES labels | `data/qualitative_sample/adjudication.xlsm`; processing/export script absent | `results/rq4/final_adjudicated.xlsx`: `Final Coding`, `Final Summary`, `Adjudicated Cases`, `Method Note` |

## Shared and historical artifacts

- `config/` and `prompts/system.txt` are shared across the RQs. `prompts/combined_examples_original.json` preserves the original combined demonstration file; per-profile JSONs contain its unchanged demonstration values.
- `vendor/aqusa-core/` remains a self-contained third-party baseline, including its license, legacy requirements, inputs, and output copies. Duplicate vendor artifacts are preserved because the runner uses that layout.
- `outputs/{raw,parsed}/archive/previous_single_prompt/` and `results/archive/previous_single_prompt/` preserve the earlier run set. Their relationship to the article is not assumed; current scripts exclude them.
- `docs/history/` preserves earlier instructions and claims, including outdated paths and earlier ground-truth counts. They are provenance, not executable instructions for the reorganized package.
- `scripts/archive/mock_predictions.py` is a historical synthetic test utility; it is not an experimental method and is not invoked by the pipeline.
- The original execution manifest remains at `docs/provenance/original_experiment_manifest.json`, unchanged. New manifests record only the current reproduction environment.
- `.env`, virtual environments, caches, and credential-bearing error logs are local ignored files, not replication evidence published in Git.
