# Lanta LLM Hosting

Host Hugging Face language models on Lanta with Slurm and vLLM, connect from Windows through an auto-reconnecting SSH tunnel, and expose a protected website or OpenAI-compatible API.

## Repository Layout

```text
lanta-llm-hosting/
  website/              Browser chat application and backend proxy.
  cli/                  OpenAI-compatible command-line chat client.
  windows/tunnel/       Hidden SSH tunnel watchdog and local API tests.
  sharing/              Authenticated API gateway and Tailscale Funnel tools.
  litellm/              Preferred OpenAI-compatible gateway, keys, usage, metrics.
  openwebui/            Primary browser chat UI backed by LiteLLM.
  observability/        Prometheus, Grafana, and platform exporter.
  benchmark/            HDL benchmark cases, runner, schemas, and artifacts.
  dashboard/            Benchmark dashboard API and minimal HTML pages.
  lanta/scripts/        Generic model download, serve, submit, and test scripts.
  lanta/legacy-qwen36/  Older Qwen3.6-specific scripts kept for reference.
  docs/                 Setup, model swapping, UI, and friend usage guides.
  HOW_TO_USE.md         Command-only operations runbook.
  HOW_TO_SWAP.md        Same-endpoint model swap runbook.
```

## Quick Start

Start the hidden tunnel:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\start-lanta-vllm-tunnel.ps1
```

Start the website:

```powershell
cd website
$env:QWEN_BASE_URL="http://127.0.0.1:8000/v1"
$env:QWEN_API_KEY="EMPTY"
$env:QWEN_MODEL="qwen36-27b"
$env:SITE_PASSWORD="YOUR_SITE_PASSWORD"
npm run dev
```

Open `http://127.0.0.1:5177`.

See [HOW_TO_USE.md](HOW_TO_USE.md) for the complete operational command list and [HOW_TO_SWAP.md](HOW_TO_SWAP.md) for model swapping.

## Platform Stack

The production-oriented path is now:

```text
OpenWebUI -> LiteLLM -> local SSH tunnel -> vLLM on Lanta
```

Start order:

1. Start Lanta vLLM job.
2. Start tunnel.
3. Start LiteLLM.
4. Start OpenWebUI.
5. Start observability stack.
6. Run benchmark suite.

Key docs:

- [Architecture](docs/ARCHITECTURE.md)
- [Operations](docs/OPERATIONS.md)
- [Benchmarking](docs/BENCHMARKING.md)

The existing `website/` remains as a fallback demo UI.

## Lanta Deployment

Copy the files in `lanta/scripts/` to the remote project's `scripts/` directory. The remote project path remains:

```text
/project/zz992000-zdevb/zz992005/ub127/SiliconCraft
```

The local repository rename does not require moving downloaded models or Conda environments on Lanta.
