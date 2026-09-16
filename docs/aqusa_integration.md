# AQUSA-core integration

## What the supplied code implements

Inspection of `aqusa-core` shows that `aqusacore.py` explicitly executes analyzers for:

1. Well-formed;
2. Atomic;
3. Minimal;
4. Unique;
5. Uniform.

The flow evaluates each story for Well-formed, Atomic, Minimal, and Unique, and then evaluates Uniform after determining the dominant backlog template.

Therefore, the pipeline restricts direct AQUSA × LLM × Gold Standard comparison to these five criteria.

## Expected format

AQUSA reads a TXT file containing one User Story per line and generates messages such as:

```text
Story #6: "..."
   Defect type: minimal.indicator_repetition
   Message: ...
```

`src/normalize_aqusa.py` converts each AQUSA defect into the same binary representation used for the LLM outputs. For the five supported criteria, the absence of an AQUSA alert is normalized as `No Violation`; one or more alerts for the same criterion are normalized as `Violation`.

## Story identity

AQUSA uses line numbers, while the Gold Standard uses PP-xxx, BC-xxx, and ZO-xxx IDs. The `*_id_map.json` files explicitly map line numbers to canonical story IDs.

## Canonical dataset

The runner **does not directly use the originally uploaded TXT files** when they differ from the Gold Standard. Files under `data/canonical/` were exported from the finalized Gold Standard dataset and are used consistently by both AQUSA and the LLM pipeline.

## Environment

The original AQUSA-core README targets Python 3.7 and its legacy requirements pin NLTK 3.4.5. The package preserves the original dependency information and provides experiment-specific setup support for controlled execution in a modern environment.

Any patch required to execute AQUSA must be versioned and documented. Detection rules must not be changed during environment adaptation, because doing so would alter the baseline itself.
