# Re-execution plan

The previous single-prompt results are preserved under `results/previous_single_prompt/` for traceability. They are **not** consumed by the new normalization glob.

The new three-prompt run writes to:

- `results/raw/zero_shot/...`
- `results/raw/one_shot/...`
- `results/raw/few_shot/...`

Recommended execution order:

1. Run `python src/validate_setup.py`.
2. Run a dry test for each profile.
3. Execute Zero-shot completely and check errors.
4. Execute One-shot completely and check errors.
5. Execute Few-shot completely and check errors.
6. Normalize only after the three profiles are complete.
7. Run metrics, audit and table builder.

This separation makes restart/skip behavior safe because the prompt profile is part of the result path and parsed metadata.
