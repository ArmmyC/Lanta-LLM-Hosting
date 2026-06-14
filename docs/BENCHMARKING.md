# Benchmarking

The benchmark foundation supports HDL, RTL, testbench, and model comparison workflows.

## Smoke Dry Run

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting
python -m benchmark.runners.run_suite --suite smoke --dry-run
```

Dry-run validates cases and writes placeholder result artifacts without calling LiteLLM.

## Run Against LiteLLM

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting
$env:LITELLM_BASE_URL="http://127.0.0.1:4000/v1"
$env:LITELLM_API_KEY="sk-your-virtual-key"
python -m benchmark.runners.run_suite --suite smoke --model active-lanta-model --prompt-version rfid_low_power_v1
```

The runner:

- loads benchmark cases
- validates IDs, task types, timeouts, and evaluator config
- builds prompts
- calls LiteLLM through the OpenAI-compatible API
- stores raw responses
- extracts code blocks
- classifies missing code and static failures
- optionally runs local compile checks when `iverilog` is available
- records latency and token usage when upstream returns usage
- writes local JSON fallback results

Model benchmark failures do not cause a nonzero exit code unless:

```powershell
--fail-on-benchmark-fail
```

Invalid case files do return nonzero.

## Cases

Smoke cases:

```text
benchmark/cases/smoke/rtl_counter.yaml
benchmark/cases/smoke/testbench_counter.yaml
```

Case validation:

- `id` must match `^[a-z0-9][a-z0-9_-]{2,80}$`
- `task_type` must be `rtl_generation`, `testbench_generation`, `rtl_debugging`, or `low_power_rewrite`
- RTL generation cases require `expected_module_name`
- `timeout_seconds` must be 1 to 600

## Storage

PostgreSQL migration:

```text
benchmark/storage/migrations/001_initial.sql
```

Set PostgreSQL storage:

```powershell
$env:BENCHMARK_DATABASE_URL="postgresql://user:password@127.0.0.1:5432/lanta_llm"
```

Local JSON fallback:

```text
benchmark/results/benchmark-results.json
```

Artifacts:

```text
benchmark/artifacts/<run_id>/<case_id>/
```

Do not commit real benchmark results or artifacts unless approved. They may contain proprietary prompts or generated code.

## Dashboard API

Start:

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting\dashboard\backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8088
```

Use PostgreSQL-backed dashboard reads:

```powershell
$env:DASHBOARD_DATABASE_URL=$env:BENCHMARK_DATABASE_URL
```

API:

```text
GET /api/healthz
GET /api/benchmark/runs
GET /api/benchmark/runs/{run_id}
GET /api/benchmark/cases
GET /api/benchmark/cases/{case_id}
GET /api/benchmark/summary
GET /api/benchmark/artifacts/{result_id}/{artifact_type}
```

Minimal pages:

```text
http://127.0.0.1:8088/
http://127.0.0.1:8088/runs
http://127.0.0.1:8088/cases
```

Artifact access is restricted to paths under `benchmark/artifacts`.
