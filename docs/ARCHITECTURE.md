# Architecture

## Request Path

```text
OpenWebUI or OpenAI-compatible client
                 |
                 v
       LiteLLM :4000 (auth, alias, usage)
                 |
                 v
       SSH tunnel :8000 (Windows host)
                 |
                 v
       vLLM :8000 (Lanta compute node)
```

LiteLLM exposes `active-lanta-model` as the stable contract. The Lanta scripts
choose the actual model, tensor parallelism, context length, and reasoning
parser. The tunnel watchdog follows the active Slurm job across compute nodes.

## Operations

- OpenWebUI is the supported browser interface.
- LiteLLM owns API authentication, virtual keys, budgets, and usage metrics.
- Prometheus scrapes LiteLLM and the platform exporter.
- Grafana is the source of truth for usage and performance charts.
- The status dashboard provides health checks and admin links only.

Raw vLLM is local infrastructure and must not be exposed to users.
