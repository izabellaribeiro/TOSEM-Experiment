# Preserved execution outputs

`raw/<profile>/<model>/<project>/run_XX/` contains original `*.request.json` and `*.response.json` files. `parsed/` contains the corresponding `*.parsed.json` files. The profile names are `zero_shot`, `one_shot`, and `few_shot`; model directory labels are the original experiment labels.

`raw/AQUSA/` contains three baseline text reports. `parsed/normalized/` contains the two unified prediction CSVs (106,470 LLM rows; 910 AQUSA rows). `parsed/aggregation/majority_vote_predictions.csv` is a processed aggregation output, not an original API response.

The `archive/previous_single_prompt/` subtrees preserve the older run set. Current normalization explicitly reads only the three current prompt directories, so archived model outputs are not pooled into the article experiment.

All original output contents are preserved and hashed in [the inventory](../docs/provenance/artifact_inventory.csv). Raw data is distinguishable from parsing/normalization and final result tables. Reproduction writes separate outputs under `replication_runs/`; API collection itself writes to these execution trees and should only be performed in an independent copy for a new experiment.

Error logs may expose provider credentials and remain ignored. They are not part of the published replication outputs.
