# Compatibility Sharing Gateway

The scripts in this folder are retained for compatibility with the earlier Tailscale Funnel sharing flow.

LiteLLM is now the preferred API gateway because it supports virtual keys, usage tracking, budgets, rate limits, and Prometheus metrics.

Use this folder only when you specifically need the older authenticated gateway path.

Do not expose raw vLLM directly to the public internet.
