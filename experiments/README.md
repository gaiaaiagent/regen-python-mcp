## Experiments: GPT Actions Constraints

These files are for validating OpenAI Custom GPT Actions constraints.

- `openapi-gpt-experiment.json`: Minimal spec for quickly testing a second Action on `https://registry.regen.gaiaai.xyz`.
- `openapi-gpt-experiment-over30.json`: Intentionally **invalid** (>30 operations) to confirm the builder rejects specs over the limit.

Do not use these for production Actions. Use:
- `openapi-gpt-ledger.json`
- `openapi-gpt-koi.json`
