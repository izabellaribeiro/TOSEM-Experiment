# Preserved study results

| Directory | Interpretation |
| --- | --- |
| `rq1/metrics/`, `rq1/tables/` | Effectiveness and supported-five AQUSA comparisons |
| `rq2/tables/`, `rq2/statistical_analysis/` | Descriptive and inferential prompting results |
| `rq3/metrics/`, `rq3/tables/` | Repeated-run stability and majority-vote effectiveness |
| `rq4/final_adjudicated.xlsx` | Recorded final 30-case qualitative evaluation, summaries and agreement values |
| `archive/previous_single_prompt/` | Preserved earlier experiment artifacts requiring provenance review |

Every original result file retains its contents. Processed majority-vote predictions live in `outputs/parsed/aggregation/`; raw API outputs live in `outputs/raw/`. Original execution audit/manifest artifacts live in `docs/provenance/`.

Reproduction commands write below `replication_runs/` rather than overwriting these results. RQ3 confidence tables and a generator for every article-level display are not supplied. The RQ4 workbook is an existing final artifact, not evidence of an available executable sampling or coding pipeline.

See [TRACEABILITY.md](../docs/TRACEABILITY.md) and [MANUAL_REVIEW.md](../docs/MANUAL_REVIEW.md).
