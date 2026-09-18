# RQ4: manual selection and provenance recovery

The study author has clarified the original selection as **manual stratified, coverage-oriented selection**. Candidates were individual run-level outputs organized into TP, TN, FP and FN and inspected manually, case by case. Selection sought approximate quadrant balance and diversity across models, prompts, QUS criteria and projects. The final sample contains 8 TP, 8 TN, 7 FP and 7 FN. It is exploratory, not a statistically representative population sample. **Selection was not random and no random seed was used.** A missing seed is therefore not a reproducibility gap.

`build_sampling_manifest.py` recovers provenance for the already selected 30 cases; it is not a sample-selection algorithm and does not reproduce or replace human decisions.

```text
python -m scripts.rq4.build_sampling_manifest
```

Inputs are the final `Final Coding` worksheet, both coder `Evaluation` worksheets, normalized individual-run LLM predictions, and final human reference labels. Exact case content matching includes evidence, rationale and related story IDs. It cross-checks coder case contents, reference labels and quadrants, without editing workbooks or running macros.

Generated files in `data/qualitative_sample/`:

- `sampling_manifest.csv`: 30 cases, recovered fields, author-confirmed selection method, source status and candidate count.
- `sampling_candidate_matches.csv`: all 51 candidate run records, including ambiguous alternatives and parsed-artifact paths.
- `sampling_manifest_audit.json`: matching rules, source hashes and observed coverage.

Twenty cases have a unique matching run. Q10–Q18 and Q29 have ambiguous runs, which remain blank in the manifest. Model and prompt can still be recovered for all 30 cases because the candidates agree on those fields. A unique source match is only a claim about the preserved input snapshot; no historical selection chronology is inferred. Rerunning the command overwrites only these derived provenance files.

Follow the workbook-level steps in [REPRODUCIBILITY.md](../../docs/REPRODUCIBILITY.md). Inputs are the two coder workbooks and the adjudication workbook in `data/qualitative_sample/`; the recorded final output is `results/rq4/final_adjudicated.xlsx`.

The manual procedure is now documented, and provenance recovery can be rerun. Human case-by-case judgments are not an executable sampling algorithm. The ten ambiguous source-run IDs and the original qualitative agreement/export procedure remain unresolved. See MR05–MR08 in [MANUAL_REVIEW.md](../../docs/MANUAL_REVIEW.md).
