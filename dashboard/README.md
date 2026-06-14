# Benchmark Dashboard

Minimal benchmark dashboard backend for the Lanta LLM platform.

## Start

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\dashboard\backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8088
```

Open API:

```text
http://127.0.0.1:8088/api/healthz
http://127.0.0.1:8088/api/benchmark/runs
http://127.0.0.1:8088/api/benchmark/cases
http://127.0.0.1:8088/api/benchmark/summary
```

The first implementation reads the local JSON fallback at `benchmark/results/benchmark-results.json`. PostgreSQL migrations are provided under `benchmark/storage/migrations/` for durable deployments.
