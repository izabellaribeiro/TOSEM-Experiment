# Execution and analysis code

Invoke package modules from the repository root with `python -m`:

| Entry point | Purpose |
| --- | --- |
| `scripts.reproduce` | Saved-output reanalysis with separate output root; no model calls |
| `scripts.rq1.run_analysis` | Existing shared effectiveness, stability and aggregation calculations and descriptive tables |
| `scripts.rq2.analyze_prompting_statistics` | Original prompting inferential analysis, relocated with updated input/output defaults |
| `scripts.rq3.run_analysis` | Shared stability/aggregation pipeline, followed by the new high-confidence stable-error audit |
| `scripts.rq3.analyze_high_confidence_stable_errors` | Explicit five-run high-confidence stable-error definition, manuscript-count comparison and diagnostics |
| `scripts/rq4/README.md` | Manual inspection workflow; original sample-selection/qualitative-analysis scripts absent |
| `scripts.execution.run_llms` | Paid model API collection; raw and parsed files stored separately |
| `scripts.execution.run_aqusa` | Bundled AQUSA baseline execution |
| `scripts.execution.normalize_llm`, `scripts.execution.normalize_aqusa` | Existing normalization logic |
| `scripts.shared.validate_setup`, `scripts.shared.audit_quantitative` | Input counts and LLM coverage checks |
| `scripts.shared.create_manifest` | Current reproduction environment/inputs, not original execution metadata |
| `scripts.verify_package` | Artifact preservation and CSV equivalence checks; not a research analysis |

`shared/metrics.py` and `shared/build_quantitative_tables.py` retain the existing calculations. Their paths/imports and output routing changed; new per-RQ entry points are orchestration wrappers, not reconstructed historical scripts. The original calculations serve multiple RQs and were kept together to avoid changing their semantics.

`archive/mock_predictions.py` is an unsupported historical test utility using an old schema/path. It must not be used to create research evidence. `setup_aqusa_nltk.py` downloads baseline resources as before. `vendor/aqusa-core/` remains the original third-party implementation.

See [REPRODUCIBILITY.md](../docs/REPRODUCIBILITY.md) for commands and limitations.
