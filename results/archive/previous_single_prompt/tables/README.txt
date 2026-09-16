QUS-13 quantitative tables

Primary interpretation recommendation:
- Use mean and standard deviation across the five independent LLM runs as the primary model-performance analysis.
- Treat majority vote as a secondary aggregation analysis.
- Use F1, MCC, and balanced accuracy as headline metrics; report precision and recall to explain the trade-off.
- Accuracy should not be interpreted alone because violation prevalence is imbalanced for several QUS criteria.
- Compare AQUSA with LLMs only on Well-formed, Atomic, Minimal, Unique, and Uniform.
- Blank metric values mean the metric is mathematically undefined for that condition; do not silently replace them with zero.
- Files 15-17 are the controlled AQUSA comparison outputs. File 17 is descriptive mean across project/run rows, not a pooled micro score.

Generated files:
01 overall mean/sd across 5 runs
02 criterion mean/sd
03 QUS dimension mean/sd
04 project mean/sd
05 project x criterion mean/sd
06 project x dimension mean/sd
07-11 majority-vote analyses
12-14 run-variability summaries
15-17 controlled AQUSA comparisons
18 overall rankings by F1, MCC, and balanced accuracy
