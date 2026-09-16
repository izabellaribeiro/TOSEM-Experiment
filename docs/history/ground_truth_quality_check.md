# Ground Truth quality check before the experiment

The supplied Ground Truth contains **2,366** `story × criterion` rows:

| Label | Count |
|---|---:|
| No Violation | 1,901 |
| Violation | 214 |
| Uncertain | 251 |
| Insufficient Context | 0 |
| Total | 2,366 |

By project:

| Project | Violation | No Violation | Uncertain | Binary units used in primary metrics |
|---|---:|---:|---:|---:|
| PlanningPoker | 43 | 602 | 44 | 645 |
| BADCamp | 102 | 688 | 107 | 790 |
| Zooniverse | 69 | 611 | 100 | 680 |
| **Total** | **214** | **1,901** | **251** | **2,115** |

## Consequence

The current binary effectiveness analysis evaluates **2,115** units and excludes **251 Uncertain units** from TP/FP/FN/TN, Precision, Recall and F1.

This is not a silent conversion. The excluded units are written to `results/metrics/excluded_ground_truth_units.csv`.

For the definitive journal experiment, the preferred scenario is to adjudicate as many `Uncertain` units as methodologically defensible before freezing the final Gold Standard. If the research team intentionally preserves uncertainty, report both the number/percentage excluded and the evaluated coverage alongside every aggregate result.
