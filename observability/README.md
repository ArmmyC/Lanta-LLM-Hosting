# Observability

This stack runs Prometheus, Grafana, and a small platform exporter.

## Start

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\observability
docker compose up -d
```

## Ports

```text
Prometheus: http://127.0.0.1:9090
Grafana: http://127.0.0.1:3002
Platform exporter: http://127.0.0.1:9108
```

Grafana dashboard:

```text
Lanta LLM Operations
```

## Metrics

Prometheus scrapes:

- LiteLLM metrics from `host.docker.internal:4000/metrics`
- Platform exporter metrics from `platform-exporter:9108/metrics`

The platform exporter checks:

- LiteLLM reachability
- vLLM `/models` reachability through the tunnel
- active model name
- local CPU/RAM/disk where available
- Slurm job state where Slurm is available

If Slurm is unavailable, Slurm metrics report unknown or zero health instead of crashing.
