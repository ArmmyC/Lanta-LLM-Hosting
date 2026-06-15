# OpenWebUI

OpenWebUI is the primary browser chat UI for this project. It should call LiteLLM, not vLLM directly.

## Start

Start the Lanta model, tunnel, and LiteLLM first. Then:

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

On first launch, OpenWebUI asks you to create the first account. That first account becomes the OpenWebUI admin. This login is separate from LiteLLM API keys.

## Provider Configuration

Automatic environment configuration points OpenWebUI to:

```text
http://litellm:4000/v1
```

If configuring manually in the OpenWebUI admin panel, use:

```text
OpenAI-compatible API URL: http://host.docker.internal:4000/v1
API key: a LiteLLM virtual key or the LiteLLM master key for admin testing
```

Default model:

```text
active-lanta-model
```

The alias is backed by `qwen36-27b` in the recommended daily RTL setup. Keep using the alias in OpenWebUI so administrators can swap the one active backend model without changing user configuration.

If OpenWebUI keeps old provider settings after `.env` changes, update the provider in the OpenWebUI admin settings. Do not delete the OpenWebUI Docker volume unless you are okay losing accounts, chats, and saved settings.

OpenWebUI stores chats and users. LiteLLM and Prometheus are the source of truth for usage metrics, API keys, budgets, and request telemetry.

## Share with Tailscale Funnel

Use Funnel when friends need browser chat from outside your local machine.

Stop any old Funnel route:

```powershell
tailscale funnel --https=443 off
```

Expose OpenWebUI:

```powershell
tailscale funnel --bg --https=443 http://127.0.0.1:3000
tailscale funnel status
```

Expected status:

```text
https://armmy.tail35169a.ts.net (Funnel on)
|-- / proxy http://127.0.0.1:3000
```

Open the public URL:

```powershell
Start-Process https://armmy.tail35169a.ts.net
```

Recommended public-user setup:

1. Keep signup enabled only while inviting people.
2. Keep new users pending or manually approved.
3. Approve invited users from the OpenWebUI admin panel.
4. Disable signup after invited users have accounts.

Do not expose raw vLLM, Grafana, Prometheus, or the admin dashboard for normal chat users.
