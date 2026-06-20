# How To Use

## Start

1. Submit a model on Lanta:

   ```powershell
   ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/submit-preset.sh qwen36-27b"
   ```

2. Start the tunnel:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\windows\tunnel\start-lanta-vllm-tunnel.ps1
   ```

3. Start LiteLLM and OpenWebUI:

   ```powershell
   docker compose -f litellm/docker-compose.yml up -d
   docker compose -f openwebui/docker-compose.yml up -d
   ```

4. Open http://127.0.0.1:3000 and select `active-lanta-model`.

## Verify

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\status-lanta-vllm-tunnel.ps1
curl.exe http://127.0.0.1:4000/v1/models -H "Authorization: Bearer $env:LITELLM_MASTER_KEY"
```

For operational checks, start the observability and dashboard Compose projects
and open http://127.0.0.1:8088/status.
