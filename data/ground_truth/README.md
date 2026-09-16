# Human reference labels

`gold_standard_qus13_final.csv` is the configured reference for RQ1–RQ3 and classification-quadrant context in RQ4. It contains 2,366 unique project/story/criterion units: 303 `Violation` and 2,063 `No Violation` labels. The file retains story IDs/text, QUS dimension/criterion, decision, evidence, rationale, context usage, related story IDs and notes.

The supplied manuscript (§3.2) reports three-expert calibration through two pilots, second-pilot Fleiss' kappa 0.81, and one project annotated by each expert using the calibrated protocol. It further reports that the 251 initially `Uncertain` cases were jointly reviewed by the three experts and resolved by human consensus before LLM/AQUSA outputs were inspected.

The final label counts are directly supported by this CSV. The original independent pilot annotations and the individual decisions/consensus history for the 251 cases are not supplied, so the CSV alone does not independently prove that process. The old pre-adjudication counts survive in [historical documentation](../../docs/history/ground_truth_quality_check.md), not in a separately supplied pre-adjudication reference CSV.

The qualitative workbooks in `data/qualitative_sample/` concern a different, 30-case rationale evaluation. They must not be cited as evidence for the 251-case reference-label adjudication. No AI-assisted annotation/adjudication procedure is asserted by this package.
