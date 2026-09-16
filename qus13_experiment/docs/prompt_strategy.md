# Prompt strategy configuration

This document explains exactly what changes and what remains fixed across the three prompting conditions.

## Common system prompt

All three conditions use the same `prompts/system.txt`. It defines the model role, the binary labels (`Violation` and `No Violation`), criterion isolation, treatment of set-level criteria, confidence labels, and the required JSON schema.

The system prompt does **not** contain worked examples. Therefore, demonstrations are controlled exclusively by the selected prompt profile.

## Common criterion information

For every API call, the runner reads one criterion from `config/criteria.json` and inserts the same fields into all three prompt templates:

- criterion name;
- QUS dimension;
- scope (`individual` or `set`);
- definition;
- operational decision rule.

The same complete project backlog is then appended to the prompt.

## Zero-shot (`zero_shot`)

Template: `prompts/zero_shot.txt`

The model receives the common system prompt, criterion information, complete backlog, and task instructions. It receives **zero labeled examples**.

This condition measures performance when the model must apply the criterion directly from its definition and operational rule.

## One-shot (`one_shot`)

Template: `prompts/one_shot.txt`

The model receives everything in Zero-shot plus **one worked example for the current criterion**.

The example is loaded from `config/prompt_examples.json` and contains:

- a synthetic story;
- optional synthetic context for set-level criteria;
- expected decision;
- evidence;
- criterion-specific rationale;
- related story IDs when relevant;
- confidence.

The purpose is to show one concrete application of the decision rule without exposing any labeled example from the evaluated datasets.

## Few-shot (`few_shot`)

Template: `prompts/few_shot.txt`

The model receives everything in Zero-shot plus **four worked examples for the current criterion**.

Whenever meaningful for the criterion, the set is balanced with 2 `Violation` and 2 `No Violation` demonstrations. This avoids teaching the model only what a violation looks like and reduces demonstration-class bias.

For set-level criteria, synthetic context stories may be included so the model sees how relationships across backlog items should be handled.

## Why the examples are synthetic

Demonstrations must not be taken from PlanningPoker, BADCamp, or Zooniverse because those stories belong to the evaluated sample and are linked to the Gold Standard. Using them as demonstrations would leak labeled experimental information into the prompt.

Synthetic demonstrations keep the examples external to the test set while still operationalizing each QUS rule.

## Experimental control

The manipulated factor is:

`number of labeled demonstrations = 0 vs 1 vs 4`

Everything else is held constant within each model:

- system prompt;
- criterion definition;
- operational rule;
- project backlog;
- story order;
- task instructions;
- output schema;
- model version;
- provider-specific generation settings;
- number of runs.

This makes differences between Zero-shot, One-shot, and Few-shot interpretable as a prompting-strategy effect rather than a change in task definition.

## Example rendering flow

For a call evaluating `Atomic` on PlanningPoker, the runner performs the following steps:

1. loads the Atomic definition and decision rule from `config/criteria.json`;
2. loads the PlanningPoker canonical backlog;
3. selects `zero_shot.txt`, `one_shot.txt`, or `few_shot.txt`;
4. for One-shot/Few-shot, loads the corresponding Atomic demonstrations from `config/prompt_examples.json`;
5. renders the final user prompt;
6. sends the same system prompt plus the rendered user prompt to the selected provider;
7. requires one JSON evaluation for every story in the backlog.

Thus, a One-shot call for `Atomic` never receives a demonstration for `Minimal`, `Unambiguous`, or another criterion. Demonstrations are criterion-specific.
