# Lanta LLM Hosting Commands

Command-first runbook for starting, sharing, checking, and stopping the local hosting stack.

## Start Lanta vLLM Job

```powershell
ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/submit-preset.sh qwen36-35b-a3b"
```

## Check Lanta Job

```powershell
ssh lanta "squeue -u ub127"
ssh lanta "squeue --start -j JOB_ID"
ssh lanta "scontrol show job JOB_ID"
ssh lanta "tail -f /project/zz992000-zdevb/zz992005/ub127/SiliconCraft/logs/vllm-model-JOB_ID.out"
ssh lanta "tail -f /project/zz992000-zdevb/zz992005/ub127/SiliconCraft/logs/vllm-model-JOB_ID.err"
```

## Stop Lanta Job

```powershell
ssh lanta "scancel JOB_ID"
```

or cancel all current vLLM jobs:

```powershell
ssh lanta "scancel -n vllm-model"
```

## Keep the Lanta Job Alive

### Windows watchdog, recommended

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting
powershell -ExecutionPolicy Bypass -File .\scripts\watch-lanta-job.ps1 -Preset qwen36-35b-a3b
```

One-shot dry run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\watch-lanta-job.ps1 -Preset qwen36-35b-a3b -Once -DryRun
```

### Lanta watchdog, optional

```powershell
ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/watch-preset.sh --preset qwen36-35b-a3b"
```

One-shot dry run:

```powershell
ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/watch-preset.sh --preset qwen36-35b-a3b --once --dry-run"
```

Stop either foreground watchdog with `Ctrl+C`.

## Start Hidden Tunnel

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\start-lanta-vllm-tunnel.ps1
```

## Check Tunnel

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\status-lanta-vllm-tunnel.ps1
Invoke-RestMethod http://127.0.0.1:8000/v1/models
```

## Stop Tunnel

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\stop-lanta-vllm-tunnel.ps1
```

## Start LiteLLM

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\litellm
Copy-Item .env.example .env
notepad .env
docker compose up -d
```

## Check LiteLLM

```powershell
$env:LITELLM_MASTER_KEY="sk-your-key"
curl.exe http://127.0.0.1:4000/v1/models -H "Authorization: Bearer $env:LITELLM_MASTER_KEY"
```

## Start OpenWebUI

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\openwebui
Copy-Item .env.example .env
notepad .env
docker compose up -d
Start-Process http://127.0.0.1:3000
```

## Start Observability

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\observability
Copy-Item .env.example .env
notepad .env
docker compose up -d
```

Open:

```text
Grafana:    http://127.0.0.1:3002
Prometheus: http://127.0.0.1:9090
Exporter:   http://127.0.0.1:9108/healthz
```

## Start Admin Dashboard

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\dashboard
Copy-Item .env.example .env
notepad .env
docker compose up -d --build
Start-Process http://127.0.0.1:8088/status
```

## Check Full Platform

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting
$env:LITELLM_MASTER_KEY="sk-your-key"
powershell -ExecutionPolicy Bypass -File .\scripts\check-platform.ps1
```

## Share OpenWebUI with Tailscale Funnel

Stop any old Funnel route first:

```powershell
tailscale funnel --https=443 off
```

Start Funnel to OpenWebUI:

```powershell
tailscale funnel --bg --https=443 http://127.0.0.1:3000
tailscale funnel status
Start-Process https://armmy.tail35169a.ts.net
```

Expected status:

```text
https://armmy.tail35169a.ts.net (Funnel on)
|-- / proxy http://127.0.0.1:3000
```

Stop public Funnel:

```powershell
tailscale funnel --https=443 off
```

## Create LiteLLM User Key

```powershell
$env:LITELLM_MASTER_KEY="sk-your-key"
curl.exe http://127.0.0.1:4000/key/generate `
  -H "Authorization: Bearer $env:LITELLM_MASTER_KEY" `
  -H "Content-Type: application/json" `
  -d "{\"models\":[\"active-lanta-model\"],\"max_budget\":10,\"metadata\":{\"user\":\"friend-name\"}}"
```

User settings:

```text
Base URL: http://<host>:4000/v1
Model: active-lanta-model
API key: sk-user-key
```

## Stop Local Stack

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\dashboard
docker compose down

cd ..\observability
docker compose down

cd ..\openwebui
docker compose down

cd ..\litellm
docker compose down
```

## Legacy Website, Optional

The old `website/` and `sharing/` flows remain for compatibility. New users should use OpenWebUI for chat and LiteLLM virtual keys for API access.

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\website
$env:QWEN_BASE_URL="http://127.0.0.1:8000/v1"
$env:QWEN_API_KEY="EMPTY"
$env:QWEN_MODEL="qwen36-27b"
$env:SITE_PASSWORD="YOUR_SITE_PASSWORD"
npm run dev
```

```powershell
Start-Process http://127.0.0.1:5177
```
