# How To Swap Models

Clients always use `active-lanta-model`; only the vLLM backend changes.

## Submit A Preset

```powershell
ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/submit-preset.sh qwen36-27b"
```

Available presets are listed by:

```powershell
ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/submit-preset.sh"
```

Supported presets:

- `qwen36-27b` (recommended default)
- `qwen36-35b-a3b`
- `qwen3-coder-30b-a3b`
- `qwen25-coder-32b`
- `deepseek-coder-v2-lite`

The tunnel watchdog detects when the running job moves to another compute node
and reconnects automatically. Verify the complete path after a swap:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\tunnel\status-lanta-vllm-tunnel.ps1
curl.exe http://127.0.0.1:8000/v1/models
curl.exe http://127.0.0.1:4000/v1/models -H "Authorization: Bearer $env:LITELLM_MASTER_KEY"
```

OpenWebUI users continue selecting `active-lanta-model`; no provider changes
are required.
