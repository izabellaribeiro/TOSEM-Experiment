# Dataset provenance and consistency check

The experiment uses the stories exported from the finalized Ground Truth workbook as the canonical input.
This prevents AQUSA/LLM evaluation from silently using text that differs from the labeled reference.

| Project | Uploaded TXT stories | Ground Truth stories | Exact positional matches | Decision |
|---|---:|---:|---:|---|
| PlanningPoker | 54 | 53 | 25 | Canonical Ground Truth export is used |
| BADCamp | 69 | 69 | 69 | Canonical Ground Truth export is used |
| Zooniverse | 81 | 60 | 0 | Canonical Ground Truth export is used |

Observed discrepancies:
- BADCamp: the uploaded TXT matches the Ground Truth stories positionally.
- PlanningPoker: the uploaded TXT has 54 lines while the Ground Truth has 53 stories; wording also diverges from the Ground Truth in later lines.
- Zooniverse: the uploaded TXT has 81 stories and materially differs from the 60-story Ground Truth dataset.

Therefore, `data/canonical/*.txt` is the only input used by the experiment runner.