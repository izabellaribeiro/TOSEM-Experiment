# Cost and scale note — current 3-model configuration

## Experimental scale

- 3 model families: GPT-5 Mini, Gemini 3.1 Pro Preview, DeepSeek V4 Pro.
- 3 projects / 182 User Stories.
- 13 QUS criteria.
- 3 prompt profiles.
- 5 runs per condition.
- **1,755 API calls** total.
- **106,470 story-level classifications** total.
- Per model: **585 calls** and **35,490 classifications**.

## OpenAI

GPT-5 Mini pricing checked during experiment preparation: $0.25 / 1M input tokens and $2.00 / 1M output tokens. Based on the token volume observed in the previous OpenAI run, the complete GPT-5 Mini portion is expected to be roughly in the **$6–$7** range. This is an estimate, not a guaranteed charge; actual output/reasoning token use can vary.

## DeepSeek

DeepSeek V4 Pro remains the configured DeepSeek model. Actual cost depends on token volume and the provider's peak/off-peak pricing at execution time. The earlier empirical token volume suggests budgeting roughly **$20** for the full three-prompt, five-run portion, with a small safety margin recommended.

## Gemini

Gemini 3.1 Pro Preview remains unchanged. Its cost is intentionally not used as a budget constraint in this package note; record actual usage from the provider dashboard after each pilot batch.

## Safer execution strategy

Before launching all 1,755 calls, run one criterion/project/run under all three prompt profiles for each model. Confirm JSON validity and inspect actual provider billing. Then extrapolate the observed cost before continuing the complete run.

Official references:

- GPT-5 Mini: https://developers.openai.com/api/docs/models/gpt-5-mini
- Gemini 3.1 Pro Preview: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview
- DeepSeek pricing/models: https://api-docs.deepseek.com/quick_start/pricing/
