# Organization validation

Validation was performed on the `replication-package-organization` working branch, starting from revision `336deaf22fc56b6d5aabcd7d17d7f76e98e9b7f5`. This is a package-maintenance record, not an additional experiment.

| Check | Observed result |
| --- | --- |
| Original tracked-file inventory | 7,749 files accounted for; 7,723 moved, including 12 filename changes |
| Unchanged original contents | 7,735 files match preorganization working-file SHA-256 values |
| Deliberately updated original files | 14 code/configuration files; original paths/hashes retained in the inventory and Git history |
| Duplicate preservation | All 518 original byte-identical groups retained |
| Input validation | 182 canonical stories, 13 criteria, 2,366 reference units |
| Final reference labels | 303 `Violation`, 2,063 `No Violation` |
| Demonstration separation | Per-profile example values equal exact subsets of the preserved original combined JSON |
| Prompt rendering | All 117 projectâ€“criterionâ€“profile rendered prompts equal the original renderer's output; no API calls made |
| LLM normalization | 106,470 rows regenerated from preserved parsed JSONs |
| AQUSA normalization | 910 rows regenerated from the three preserved reports |
| Quantitative audit | PASS for row count, profiles, models, duplicate keys and repeated-run coverage |
| Quantitative reanalysis | All 25 corresponding preserved normalized/aggregation/result CSVs equal regenerated CSV contents, including field values and duplicate rows; row ordering is not treated as meaningful |
| Protected output roots | Repository root and preserved data/output/result/documentation locations rejected by the shared reproduction output-root validator |
| RQ4 artifact inspection | 30 distinct final Case IDs; their reference labels agree with the final Gold Standard; all have at least one matching normalized output |
| RQ4 source ambiguity | 20 cases have one exact text match; 10 have multiple matching run records; no unique source key assigned to ambiguous cases |

The available quantitative pipeline was run with:

```text
python -m scripts.reproduce --output-root replication_runs/organization_check
python -m scripts.verify_package --reproduced-root replication_runs/organization_check
```

Generated checks remain local under the ignored `replication_runs/organization_check/` directory. Preserved CSVs and workbooks were not overwritten. `.gitattributes` disables automatic newline conversion so preserved SHA-256 values remain meaningful after checkout on other operating systems.

Active Python syntax, current Markdown links, and Git whitespace checks were also inspected. Historical documentation deliberately retains obsolete path references and is excluded from current-link validation.

No new API collection, AQUSA detection run, human coding, confidence analysis, sample selection, or missing manuscript table/figure generation was performed. RQ4 values were read from existing workbook XML without executing macros. Known gaps are listed in [MANUAL_REVIEW.md](MANUAL_REVIEW.md).
