# Model snapshot used in the default configuration

Checked for experiment preparation on 2026-09-01.

- OpenAI: `gpt-5-mini` (GPT-5 Mini).
- Google Gemini: `gemini-3.1-pro-preview` (Gemini 3.1 Pro Preview).
- DeepSeek: `deepseek-v4-pro` (DeepSeek V4 Pro).

The default configuration intentionally uses one representative model per provider family.

## API compatibility note

GPT-5 Mini supports the Responses API but does not accept the `temperature` field. The runner therefore omits that field only for GPT-5 Mini. Gemini and DeepSeek keep `temperature=0`. This provider-specific difference is fixed across Zero-shot, One-shot, and Few-shot, so prompting remains the manipulated factor within each model.

Provider documentation changes over time. Before the definitive experimental run, verify availability again and freeze the exact model identifier/date. Prefer version-pinned snapshots when the provider exposes them and record the actual model identifier returned by the API.

Official references:

- GPT-5 Mini: https://developers.openai.com/api/docs/models/gpt-5-mini
- Gemini 3.1 Pro Preview: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview
- DeepSeek models: https://api-docs.deepseek.com/quick_start/pricing/
