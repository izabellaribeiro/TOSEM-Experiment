# Frozen prompting conditions

`system.txt` is shared by all conditions. Templates are preserved byte-for-byte from the original package:

| Profile | Template | Demonstrations |
| --- | --- | --- |
| `zero_shot` | `zero_shot/template.txt` | None |
| `one_shot` | `one_shot/template.txt` | `one_shot/examples.json`: one per criterion |
| `few_shot` | `few_shot/template.txt` | `few_shot/examples.json`: four per criterion |

The new per-profile JSONs are exact extractions of the original demonstration values in `combined_examples_original.json`, which is retained unchanged for provenance. `python -m scripts.verify_package` verifies equality. The execution runner reads the separated files and reconstructs the original criterion-wise rendering inputs.

Demonstrations are synthetic and external to the evaluated projects. Definitions and operational rules come from `config/criteria.json`; dataset IDs/paths and profile selection come from `config/experiment.json`. This organization does not change the prompt text or add demonstrations. Existing requests in `outputs/raw/` preserve the rendered experimental prompts.

The common inputs support RQ1–RQ4; the controlled comparison between profiles addresses RQ2 specifically. See [traceability](../docs/TRACEABILITY.md).
