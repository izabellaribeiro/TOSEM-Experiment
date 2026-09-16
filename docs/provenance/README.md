# Provenance records

- `artifact_inventory.csv`: exhaustive mapping of the 7,749 originally tracked working files, original SHA-256/size, current location, scope, operation and preservation status. Hashes describe the files inspected before organization; automatic newline normalization is disabled in the reorganized repository.
- `duplicate_files.csv`: original byte-identical groups, retaining each original/current path. Duplicate files are not deduplicated.
- `organization_summary.json`: counts derived from the mapping, not experimental result values.
- `original_experiment_manifest.json`: unchanged historical environment/configuration record, including its unresolved old Gold Standard path.
- `execution_audit/audit_summary.json`: unchanged original quantitative coverage audit.
- `manuscript_reference.json`: identifier and SHA-256 of the user-supplied manuscript consulted for RQ/stage mapping. The manuscript itself is not added to the repository.

New reproduction manifests are written below the selected local output root. They are distinct from original execution metadata. Source and documentation edits remain traceable through Git history; immutable artifact hashes are checked by `python -m scripts.verify_package`.
