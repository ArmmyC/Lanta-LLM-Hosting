# Lanta LLM Platform Operations

## Startup Order

1. Start Lanta vLLM job.
2. Start tunnel.
3. Start LiteLLM.
4. Start OpenWebUI.
5. Start observability stack.
6. Run benchmark suite.

## 1. Start Lanta vLLM

```powershell
ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/submit-preset.sh qwen36-35b-a3b"
```

Check status:

```powershell
ssh lanta "squeue -u ub127"
```

## 2. Start Tunnel

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\start-lanta-vllm-tunnel.ps1
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\status-lanta-vllm-tunnel.ps1
```

Expected endpoint:

```text
http://127.0.0.1:8000/v1
```

## 3. Start LiteLLM

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\litellm
Copy-Item .env.example .env
notepad .env
docker compose up -d
```

Verify:

```powershell
curl.exe http://127.0.0.1:4000/v1/models -H "Authorization: Bearer $env:LITELLM_MASTER_KEY"
```

## 4. Start OpenWebUI

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\openwebui
Copy-Item .env.example .env
notepad .env
docker compose up -d
```

Open:

```text
http://127.0.0.1:3000
```

If automatic provider configuration fails, add an OpenAI-compatible provider manually:

```text
Base URL: http://host.docker.internal:4000/v1
API key: LiteLLM virtual key
```

## 5. Start Observability

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\observability
docker compose up -d
```

Ports:

```text
Prometheus: http://127.0.0.1:9090
Grafana: http://127.0.0.1:3002
Platform exporter: http://127.0.0.1:9108
```

Grafana dashboard:

```text
Lanta LLM Operations
```

## LiteLLM Virtual Keys

Create:

```powershell
curl.exe http://127.0.0.1:4000/key/generate `
  -H "Authorization: Bearer $env:LITELLM_MASTER_KEY" `
  -H "Content-Type: application/json" `
  -d "{\"models\":[\"active-lanta-model\"],\"max_budget\":10}"
```

List:

```powershell
curl.exe http://127.0.0.1:4000/key/list -H "Authorization: Bearer $env:LITELLM_MASTER_KEY"
```

Revoke:

```powershell
curl.exe http://127.0.0.1:4000/key/delete `
  -H "Authorization: Bearer $env:LITELLM_MASTER_KEY" `
  -H "Content-Type: application/json" `
  -d "{\"keys\":[\"sk-user-key\"]}"
```

“API generation” means creating and managing LiteLLM virtual keys.

## Compatibility Gateways

The existing `website/` and `sharing/` flows remain available for demos and compatibility. LiteLLM is now the preferred gateway for new users, scripts, and benchmark runs.

