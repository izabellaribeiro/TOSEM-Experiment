# Experimental design — QUS-13 × three prompting strategies

## 1. Objective

Evaluate the effectiveness, stability, and explanatory quality of different LLMs in detecting violations of the 13 QUS criteria using a human-established Gold Standard, while treating **prompting strategy** as an explicit experimental factor.

## 2. Experimental factors

- 3 LLMs, one representative per provider family: GPT-5 Mini (OpenAI), Gemini 3.1 Pro Preview (Google), and DeepSeek V4 Pro (DeepSeek);
- 3 projects: PlanningPoker (53 stories), BADCamp (69 stories), and Zooniverse (60 stories);
- 13 QUS criteria;
- 3 prompting strategies: Zero-shot, One-shot, and Few-shot;
- 5 independent runs per condition;
- generation parameters kept fixed within each model across the three prompt conditions. Gemini and DeepSeek use `temperature = 0`; GPT-5 Mini omits `temperature` because this model does not accept that parameter through the configured API.

Total LLM calls: `3 × 3 × 13 × 3 × 5 = 1,755`.

Each API call receives one complete project backlog and one QUS criterion, and returns one evaluation for every story in that backlog. Therefore, each prompt strategy produces `3 × 5 × 182 × 13 = 35,490` story×criterion×run classifications; the three strategies together produce 106,470 classifications.

## 3. Prompt engineering

The criterion-wise task structure is held constant across all conditions. The **only deliberate prompt manipulation is the number of labeled demonstrations**.

### P0 — Zero-shot

The model receives:

- the criterion name;
- QUS dimension and scope;
- criterion definition;
- operational decision rule;
- the complete project backlog;
- the classification task;
- the required JSON output schema through the common system prompt;
- **no labeled demonstration**.

### P1 — One-shot

P1 contains exactly the same information as P0, plus **one criterion-specific worked demonstration**. The demonstration includes a synthetic User Story, its expected `Violation` or `No Violation` decision, evidence, rationale, related story IDs when relevant, and confidence.

The demonstration is synthetic and external to PlanningPoker, BADCamp, and Zooniverse.

### P4 — Few-shot

P4 contains exactly the same information as P0, plus **four criterion-specific worked demonstrations**. Whenever the criterion permits a meaningful balance, the four demonstrations contain:

- 2 `Violation` examples;
- 2 `No Violation` examples.

For set-level criteria, demonstrations may also include a small synthetic context containing related User Stories so that the model sees how cross-story comparison should be performed.

All demonstrations are synthetic and external to the experimental datasets.

### Why this configuration is controlled

The purpose is to isolate the effect of demonstration quantity. Across P0, P1, and P4, the following remain unchanged:

- model version;
- project/backlog;
- story order and IDs;
- QUS criterion definition;
- operational decision rule;
- system prompt;
- output labels;
- output JSON schema;
- provider-specific generation settings;
- five-run protocol;
- Gold Standard and exclusion policy.

The examples are frozen in `config/prompt_examples.json`. No User Story from PlanningPoker, BADCamp, or Zooniverse is used as a demonstration, preventing label leakage from the evaluated datasets.

## 4. Proposed Research Questions

**RQ1 — Effectiveness.** How effectively do LLMs identify violations of the 13 QUS criteria compared with a human Gold Standard?

**RQ2 — QUS factors.** How does effectiveness vary across QUS criteria, dimensions, and project backlogs?

**RQ3 — Prompting.** How do Zero-shot, One-shot, and Few-shot prompting affect LLM effectiveness in QUS assessment?

**RQ4 — Stability.** How do model and prompting strategy affect consistency across five repeated executions, and does majority voting improve effectiveness?

**RQ5 — AQUSA baseline.** How do LLM configurations compare with AQUSA on the five QUS criteria supported by both approaches?

**RQ6 — Confidence.** To what extent does self-reported LLM confidence reflect correctness and cross-run stability, and does this relationship vary by prompting strategy?

**RQ7 — Qualitative errors.** What reasoning patterns characterize TP, TN, FP, and FN cases, including correct classifications supported by incorrect or weak rationales?

## 5. Controlled comparison rules

To attribute differences to prompting, keep constant across P0/P1/P4:

- model version;
- project/backlog;
- story order and IDs;
- criterion definition and operational rule;
- generation parameters supported by each model, fixed across P0/P1/P4;
- output JSON schema;
- five-run protocol;
- binary output labels;
- Gold Standard and exclusion policy.

Do not change model parameters between prompting conditions unless the change becomes a separately declared experimental factor.

## 6. Primary analysis

Report effectiveness by `prompt_profile × model`, with mean and standard deviation over the five runs. Headline metrics are F1, MCC, Balanced Accuracy, Precision, and Recall. Accuracy is secondary because the Gold Standard is imbalanced.

For the prompting RQ, do not pool the three strategies before comparing them. Compare each strategy separately within each model and then inspect whether the prompt effect is consistent across models, criteria, and projects.

## 7. Stability and confidence

Compute Jaccard, unanimous-unit rate, flip rate, and Fleiss' Kappa separately for each `prompt_profile × model × project × criterion`. Majority vote is a secondary aggregation analysis.

Self-reported `High/Moderate/Low` confidence is not treated as a calibrated probability. Compare it with correctness and cross-run agreement (5/5, 4/5, 3/5), and identify stable high-confidence errors.

## 8. AQUSA

AQUSA remains deterministic and is compared directly only on Well-formed, Atomic, Minimal, Unique, and Uniform. AQUSA is not duplicated across prompt profiles because prompting does not apply to it.

## 9. Reproducibility

Every raw request, raw response, and parsed output is saved under:

`results/raw/<prompt_profile>/<model>/<project>/run_XX/<criterion>.*`

This structure prevents results from different prompt strategies from being mixed or overwritten.
