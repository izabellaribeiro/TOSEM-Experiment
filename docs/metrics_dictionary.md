# Metrics dictionary

Treat `Violation` as the positive class.

- **TP (True Positive):** Gold Standard = Violation and method = Violation.
- **FP (False Positive):** Gold Standard = No Violation and method = Violation.
- **FN (False Negative):** Gold Standard = Violation and method = No Violation.
- **TN (True Negative):** Gold Standard = No Violation and method = No Violation.
- **Precision:** TP / (TP + FP). Among reported violations, the proportion that are real violations.
- **Recall / Sensitivity:** TP / (TP + FN). Among real violations, the proportion detected.
- **F1:** harmonic mean of Precision and Recall.
- **Specificity:** TN / (TN + FP). Ability to avoid reporting a defect when none is present.
- **Accuracy:** (TP + TN) / total.
- **Balanced Accuracy:** mean of Recall and Specificity; useful under class imbalance.
- **FPR:** FP / (FP + TN).
- **FNR:** FN / (FN + TP).
- **NPV:** TN / (TN + FN).
- **MCC:** correlation between prediction and reference label, robust to class imbalance.

## Variability metrics

- **Pairwise Jaccard:** overlap between sets of units classified as Violation in two runs.
- **Unanimous unit rate:** proportion of units receiving the same decision in all five runs.
- **Flip rate:** 1 - unanimous unit rate.
- **Violation frequency:** number of runs classifying a unit as Violation divided by the number of available runs; values near 0.5 indicate local instability.
- **Fleiss' Kappa across runs:** agreement beyond chance, treating the five runs as five binary raters.
- **Majority vote:** aggregated decision from the majority of the five runs.

## Recommended aggregation for the paper

Report at least:

1. metrics by project and model, with mean ± standard deviation across five runs;
2. metrics by criterion;
3. global micro-average;
4. macro-average across criteria, derived from criterion-level results;
5. majority-vote results as a complementary analysis rather than a replacement for individual runs;
6. FP/FN distribution by criterion and project;
7. evaluated coverage after excluding non-binary Gold Standard labels.
