# Three-prompt protocol

All conditions use criterion-wise backlog evaluation and the same system prompt/output schema.

- `zero_shot.txt`: 0 worked demonstrations.
- `one_shot.txt`: 1 criterion-specific synthetic worked demonstration.
- `few_shot.txt`: 4 criterion-specific synthetic demonstrations (2 Violation + 2 No Violation whenever applicable).

Demonstrations are defined in `config/prompt_examples.json` and are deliberately external to PlanningPoker, BADCamp and Zooniverse to avoid label leakage.

The experimental manipulation is the number of demonstrations. Definitions, operational rules, dataset context, temperature, task, and output schema remain fixed.
