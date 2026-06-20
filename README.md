# Lanta LLM Hosting

Infrastructure for serving one active Hugging Face model on Lanta through vLLM,
LiteLLM, and OpenWebUI.

## Architecture

```text
OpenWebUI / API clients
          |
          v
       LiteLLM
          |
          v
 Windows SSH tunnel
          |
          v
   vLLM on Lanta
```

The stable client-facing model name is `active-lanta-model`. Administrators can
swap its vLLM backend without changing client configuration.

| Service | Local URL |
| --- | --- |
| OpenWebUI | http://127.0.0.1:3000 |
| LiteLLM | http://127.0.0.1:4000/v1 |
| vLLM tunnel | http://127.0.0.1:8000/v1 |
| Status dashboard | http://127.0.0.1:8088/status |
| Grafana | http://127.0.0.1:3002 |
| Prometheus | http://127.0.0.1:9090 |

## Quick Start

Submit the recommended model:

```powershell
ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/submit-preset.sh qwen36-27b"
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\start-lanta-vllm-tunnel.ps1
```

Start the local services:

```powershell
docker compose -f litellm/docker-compose.yml up -d
docker compose -f openwebui/docker-compose.yml up -d
docker compose -f observability/docker-compose.yml up -d
docker compose -f dashboard/docker-compose.yml up -d --build
```

Check the platform:

```powershell
$env:LITELLM_MASTER_KEY = "sk-your-key"
powershell -ExecutionPolicy Bypass -File .\scripts\check-platform.ps1
```

## Repository Layout

| Path | Purpose |
| --- | --- |
| `lanta/scripts/` | Model download, submission, serving, and job watchdogs |
| `windows/tunnel/` | Self-healing SSH tunnel to the active Slurm node |
| `litellm/` | Stable OpenAI-compatible gateway |
| `openwebui/` | OpenWebUI deployment configuration |
| `observability/` | Prometheus, Grafana, and platform exporter |
| `dashboard/` | Admin health/status service |
| `sharing/` | Authenticated sharing and Tailscale Funnel helpers |
| `cli/` | Command-line chat clients |

Benchmark development lives in
[ArmmyC/RLTBench](https://github.com/ArmmyC/RLTBench).

## Documentation

- [Operations](docs/OPERATIONS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Model swapping](HOW_TO_SWAP.md)
- [Key management](docs/KEY_MANAGEMENT.md)
- [OpenWebUI](openwebui/README.md)

Do not expose raw vLLM, Prometheus, Grafana, or the status dashboard publicly.
Use OpenWebUI for browser users and LiteLLM virtual keys for API users.
