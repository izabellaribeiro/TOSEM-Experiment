# Model selection for the rerun

The rerun uses one representative model from each provider family:

| Provider family | Model | API model ID |
|---|---|---|
| OpenAI | GPT-5 Mini | `gpt-5-mini` |
| Google | Gemini 3.1 Pro Preview | `gemini-3.1-pro-preview` |
| DeepSeek | DeepSeek V4 Pro | `deepseek-v4-pro` |

This selection replaces the previous two-OpenAI-model configuration (GPT-4.1 and GPT-5.2) with a single cost-efficient OpenAI representative while preserving Google and DeepSeek as independent provider families.

## Experimental size

`3 models × 3 projects × 13 criteria × 3 prompt profiles × 5 runs = 1,755 API calls`

`3 models × 182 stories × 13 criteria × 3 prompt profiles × 5 runs = 106,470 classifications`

## Provider-specific reproducibility note

The experiment keeps the same prompt content and condition structure across providers. Provider API parameters that are not mutually supported are recorded rather than forced. In particular, GPT-5 Mini does not accept `temperature`; the request therefore omits this field for that model. Gemini and DeepSeek continue to use the configured temperature value of 0.
