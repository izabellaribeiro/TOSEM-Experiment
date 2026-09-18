# RQ4 qualitative sample

These workbooks are preserved byte-for-byte; only filenames and directories changed:

| Current file | Original file | Role |
| --- | --- | --- |
| `qualitative_evaluation_coder1.xlsx` | `QUS13_Qualitative_Evaluation_Coder1.xlsx` | Coder 1 instructions, 30 evaluation cases, codebook, backlog reference |
| `qualitative_evaluation_coder2.xlsx` | `QUS13_Qualitative_Evaluation_Coder2.xlsx` | Coder 2 version of the same materials |
| `adjudication.xlsm` | `Adjudication.xlsm` | Recorded qualitative disagreements and adjudicated RC/ES decisions |

The final workbook is [results/rq4/final_adjudicated.xlsx](../../results/rq4/final_adjudicated.xlsx). Its `Final Coding` sheet contains Q01–Q30; `Final Summary` records the resulting counts and agreement statistics. Formatting-only spreadsheet rows are not additional sample cases.

## Author-clarified selection procedure

The study author has clarified that the original procedure was **manual stratified, coverage-oriented selection**, not random sampling. **No random seed was used.** Candidate individual run-level outputs were organized into TP, TN, FP and FN, inspected manually case by case, and selected to keep the four quadrants approximately balanced while increasing diversity across models, prompting strategies, QUS criteria and project backlogs. The final sample has **8 TP, 8 TN, 7 FP and 7 FN**. Its purpose is exploratory coverage of heterogeneous behaviors, not population-level statistical representativeness. Observed equal coverage by model/prompt/project below is a recovered property of the final sample, not an inferred selection quota.

## Recovered provenance

- [sampling_manifest.csv](sampling_manifest.csv): one row per existing Case ID, with `selection_method = manual_stratified_coverage_selection`.
- [sampling_candidate_matches.csv](sampling_candidate_matches.csv): all 51 matching individual-run records, including alternatives for ambiguous cases, their parsed-artifact paths, and their normalized CSV record numbers (header counted as record 1; not physical text line numbers).
- [sampling_manifest_audit.json](sampling_manifest_audit.json): source SHA-256 values, matching fields, status counts, and coverage summaries. This is a new provenance-recovery record, not a historical sampling log.

The workbooks omit model, prompt and run identifiers. Matching uses exact project, story ID, criterion, prediction, evidence and rationale, plus the parsed JSON list of related story IDs. Both coder workbooks are checked against `Final Coding`; story text, human labels and recorded quadrants are checked against the final reference. Workbook contents are never changed.

All 30 cases have supported values for case ID, quadrant, model, prompt, project, story ID, criterion, ground truth and prediction. Model/prompt values are populated only when all candidates agree. The selection-method value comes from the author's clarification, not from inferred model output.

Twenty cases have one match (`source_status = unique_match`). **Q10, Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q18 and Q29** have multiple matching runs (`source_status = ambiguous`); their `run` fields remain blank. Candidate records are not additional sample cases. A unique match establishes uniqueness within the preserved normalized snapshot, not an independently recovered historical selection log. The ten ambiguous source-run identifiers still require the author's original records.

Observed coverage: 10 cases per model (DeepSeek V4 Pro, GPT-5 Mini, Gemini 3.1 Pro Preview), 10 per prompting strategy, and 10 per project. All 13 QUS criteria occur; detailed counts are in the audit JSON.

To regenerate the provenance files from the fixed workbooks and normalized data:

```text
python -m scripts.rq4.build_sampling_manifest
```

This command rewrites only the three derived provenance files listed above. It neither selects a new sample nor attempts to replay human inspection. It uses the Python standard library and existing repository helpers; workbook macros are not executed.

Consult the [manual RQ4 workflow](../../docs/REPRODUCIBILITY.md) and [review register](../../docs/MANUAL_REVIEW.md). Do not execute workbook macros or alter original coding merely to inspect the recorded artifacts. These workbooks are unrelated to the 251-case Gold Standard consensus process.
