# Operations

## Startup Order

1. Submit or confirm the Lanta vLLM job.
2. Start the Windows tunnel.
3. Start LiteLLM.
4. Start OpenWebUI.
5. Start observability and the status dashboard.

```powershell
ssh lanta "squeue -u ub127"
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\start-lanta-vllm-tunnel.ps1
docker compose -f litellm/docker-compose.yml up -d
docker compose -f openwebui/docker-compose.yml up -d
docker compose -f observability/docker-compose.yml up -d
docker compose -f dashboard/docker-compose.yml up -d --build
```

## Health Checks

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\status-lanta-vllm-tunnel.ps1
$env:LITELLM_MASTER_KEY = "sk-your-key"
powershell -ExecutionPolicy Bypass -File .\scripts\check-platform.ps1
```

Use:

- http://127.0.0.1:8088/status for component health.
- http://127.0.0.1:3002 for usage, latency, tokens, and errors.
- http://127.0.0.1:9090 for raw Prometheus queries.

## Recovery

- No Slurm job: submit a preset from `lanta/scripts/submit-preset.sh`.
- Tunnel offline: run the stop script, then the start script.
- LiteLLM model missing: verify its key, config, and tunnel health.
- OpenWebUI provider stale: point it to `http://litellm:4000/v1` and retain
  `active-lanta-model`.

Do not delete OpenWebUI volumes unless loss of users, chats, and settings is
acceptable. Do not commit `.env` files or secret keys.
