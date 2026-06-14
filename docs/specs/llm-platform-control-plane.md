# Feature Spec: LLM Platform Control Plane and Benchmark Dashboard Foundation

## 1. Goal

Build a production-oriented internal LLM platform around the existing Lanta/vLLM hosting repo.

The platform should add:

1. **OpenWebUI** as the main user-facing chat UI.
2. **LiteLLM Proxy** as the central OpenAI-compatible API gateway for API keys, model routing, usage tracking, budgets, and rate limits.
3. **Prometheus + Grafana** as the operations dashboard for concurrent requests, token usage, token/s, latency, RAM usage, GPU usage, tunnel status, and Slurm/vLLM health.
4. **A custom benchmark/evaluation foundation** for HDL, RTL, testbench, and model comparison workflows.
5. **A benchmark dashboard API and data model** that Codex can extend later into a full evaluation UI.

The current repository already hosts Hugging Face models on Lanta through Slurm/vLLM and exposes a website or OpenAI-compatible API.  The new feature should evolve the repo from a model-hosting prototype into a private LLM platform for IC design and HDL benchmarking.

OpenWebUI should connect to LiteLLM using the OpenAI-compatible API flow, because OpenWebUI officially supports servers implementing the OpenAI-compatible API and is built around the Chat Completions protocol. ([Open WebUI][1]) LiteLLM should sit between OpenWebUI and vLLM because LiteLLM supports virtual keys and usage controls. ([LiteLLM][2]) LiteLLM metrics should be scraped by Prometheus, because LiteLLM exposes Prometheus metrics when configured. ([LiteLLM][3])

## 2. Non-goals

This task should **not** build:

1. A replacement for OpenWebUI’s full chat interface.
2. A custom authentication system for OpenWebUI.
3. A full public SaaS billing system.
4. A polished external customer portal.
5. Full synthesis-based area/power analysis in the first implementation.
6. Multi-tenant enterprise RBAC beyond basic admin/user separation.
7. A complete benchmark case library.
8. A custom alternative to LiteLLM virtual keys.
9. A full rewrite of existing Lanta Slurm scripts.
10. A full replacement of the existing `website/` folder. Keep it as a fallback/demo UI.

## 3. Assumptions

1. The repository remains named `Lanta-LLM-Hosting`.
2. The current Lanta/vLLM flow remains the inference backend.
3. The local vLLM endpoint is still exposed through the existing SSH tunnel at:

```text
http://127.0.0.1:8000/v1
```

4. Only one vLLM model is served on port `8000` at a time in the current setup. The existing model swap docs say swapping cancels the previous `vllm-model` job and starts a new one on the same endpoint. 
5. OpenWebUI should be the main UI for human users.
6. LiteLLM should be the main gateway for OpenAI-compatible API access.
7. The existing `sharing/authenticated-openai-gateway.mjs` can remain temporarily, but LiteLLM should become the preferred API gateway.
8. The first benchmark implementation should support compile/simulation/checker-style evaluation, but can use placeholder evaluators when local HDL tools are unavailable.
9. Prometheus should scrape metrics. Prometheus stores metrics as time-series data and uses an HTTP pull model. ([Prometheus][4])
10. Grafana should visualize metrics from Prometheus. Grafana is intended for dashboarding and visualization over external data sources. ([Grafana Labs][5])
11. Docker Compose is acceptable for local platform services.
12. PostgreSQL should be used for LiteLLM and benchmark metadata.
13. SQLite may be used only for local development fallback if PostgreSQL is unavailable.
14. Existing PowerShell scripts for tunnel management should continue working.

## 4. User stories

* As an engineer, I want to open OpenWebUI and chat with the active Lanta model, so that I can use the private model without knowing Slurm, vLLM, or SSH tunnel commands.
* As an engineer, I want the model list in OpenWebUI to show the active model, so that I can avoid sending prompts to the wrong model alias.
* As an admin, I want to create API keys through LiteLLM, so that other users or tools can call the internal LLM endpoint securely.
* As an admin, I want to see token usage per key and per model, so that I can monitor resource consumption.
* As an admin, I want to see concurrent requests, request latency, token/s, errors, and active model status, so that I can diagnose system health.
* As an admin, I want to see CPU, RAM, disk, GPU memory, GPU utilization, and tunnel status, so that I can understand whether failures are caused by infrastructure or model behavior.
* As a benchmark maintainer, I want to run HDL benchmark cases against the active model, so that I can compare model quality.
* As a benchmark maintainer, I want every benchmark result stored with prompt version, model name, token usage, generated code, compile status, simulation status, and failure reason, so that results are reproducible.
* As a benchmark maintainer, I want to compare model performance across RTL generation, testbench generation, and debugging tasks, so that I can choose the best model for SiliconCraft workflows.
* As a developer, I want a clear repo structure and docs, so that future Codex tasks can add features without guessing the architecture.

## 5. UX / UI requirements

### 5.1 OpenWebUI user experience

OpenWebUI is the primary chat UI.

Required behavior:

1. Users open OpenWebUI in a browser.
2. Users log in using OpenWebUI’s built-in user system.
3. Users select the active LiteLLM model.
4. Users chat normally.
5. OpenWebUI sends requests to LiteLLM, not directly to vLLM.
6. The existing custom `website/` remains available as a fallback demo UI.

OpenWebUI connection target:

```text
http://litellm:4000/v1
```

For local Docker on Windows, document when to use:

```text
http://host.docker.internal:4000/v1
```

### 5.2 LiteLLM admin experience

LiteLLM should expose an admin interface or documented CLI/API flow for:

1. Creating API keys.
2. Listing API keys.
3. Revoking API keys.
4. Setting allowed model aliases.
5. Setting optional budgets.
6. Viewing usage per key.
7. Viewing usage per model.

The UI must not expose the upstream vLLM API key or internal tunnel details to normal users.

### 5.3 Grafana operations dashboard

Create a Grafana dashboard folder with provisioned dashboards.

Dashboard name:

```text
Lanta LLM Operations
```

Panels required:

1. Current active model.
2. LiteLLM request rate.
3. Concurrent in-flight requests.
4. Total requests.
5. Error rate.
6. p50 latency.
7. p95 latency.
8. Input tokens/min.
9. Output tokens/min.
10. Total tokens.
11. Output token/s.
12. Usage by API key or user where available.
13. Usage by model alias.
14. LiteLLM uptime.
15. vLLM upstream health.
16. SSH tunnel health.
17. RAM usage.
18. CPU usage.
19. Disk usage.
20. GPU utilization.
21. GPU memory usage.
22. Slurm job state.
23. Active vLLM job ID.
24. Last successful health check timestamp.

States:

* Empty state: show “No metrics yet. Generate a request through OpenWebUI or LiteLLM.”
* Loading state: Grafana default loading spinner is acceptable.
* Error state: panels should show no-data or query-error clearly.
* Offline state: custom exporter should report `0` for health metrics and include labels where possible.

Responsive behavior:

* Dashboard should be readable on 1920x1080 desktop.
* Mobile support is not required for the first version.
* Panels should be grouped into rows:

  * Inference
  * Usage
  * System
  * Lanta/Slurm
  * Benchmark

### 5.4 Benchmark dashboard experience

For this task, build the backend and minimal UI foundation only.

Minimum UI can be one of:

1. Streamlit app, or
2. Simple FastAPI HTML templates, or
3. Static HTML backed by API endpoints.

Preferred first implementation:

```text
dashboard/
  backend/ FastAPI
  frontend/ simple server-rendered HTML or static minimal UI
```

Pages required:

#### Page: Benchmark Overview

Displays:

1. Total benchmark runs.
2. Latest run status.
3. Pass rate by model.
4. Compile pass rate.
5. Simulation pass rate.
6. Average latency.
7. Average token usage.
8. Common failure categories.

Empty state:

```text
No benchmark runs yet. Run `python -m benchmark.runners.run_suite --suite smoke`.
```

#### Page: Benchmark Runs

Displays table:

1. Run ID.
2. Created time.
3. Suite name.
4. Model alias.
5. Prompt version.
6. Status.
7. Cases passed.
8. Cases failed.
9. Total cases.
10. Duration.

Clicking a run opens run detail.

#### Page: Benchmark Run Detail

Displays:

1. Run metadata.
2. Case results table.
3. Generated RTL/testbench artifact links.
4. Compile logs.
5. Simulation logs.
6. Failure reason.
7. Token usage.
8. Latency.

#### Page: Case Detail

Displays:

1. Case name.
2. Task type.
3. Prompt input.
4. Expected module/interface.
5. Testbench/checker config.
6. Latest results across models.

## 6. Functional requirements

### 6.1 OpenWebUI integration

1. Add an `openwebui/` folder containing Docker Compose configuration.
2. OpenWebUI must be configured to use LiteLLM as its OpenAI-compatible provider.
3. OpenWebUI must not call vLLM directly.
4. OpenWebUI configuration must use environment variables from `.env`.
5. The docs must explain how to start OpenWebUI.
6. The docs must explain how to connect OpenWebUI to LiteLLM manually through the admin panel if automatic environment configuration fails.
7. The docs must explain that OpenWebUI handles user chats, but LiteLLM and Prometheus are the source of truth for usage metrics.

### 6.2 LiteLLM integration

8. Add a `litellm/` folder containing Docker Compose configuration.
9. Add `litellm/config.yaml`.
10. Add `litellm/.env.example`.
11. LiteLLM must expose an OpenAI-compatible API at:

```text
http://127.0.0.1:4000/v1
```

12. LiteLLM must route requests to the existing local vLLM tunnel:

```text
http://host.docker.internal:8000/v1
```

or documented equivalent for Linux.

13. LiteLLM must define at least one model alias:

```text
active-lanta-model
```

14. LiteLLM must use a master key from environment variable:

```text
LITELLM_MASTER_KEY
```

15. LiteLLM must use PostgreSQL for persistent key and usage data.
16. LiteLLM must expose metrics for Prometheus.
17. LiteLLM must log model name, request status, latency, and token usage when available.
18. LiteLLM must support virtual API keys.
19. The docs must show how to generate a user API key.
20. The docs must show how to revoke a user API key.
21. The docs must show how to call the API using curl.
22. The docs must explain that “API generation” means generating and managing LiteLLM virtual keys.

### 6.3 Observability

23. Add an `observability/` folder.
24. Add Prometheus configuration.
25. Add Grafana provisioning configuration.
26. Add at least one provisioned Grafana dashboard JSON.
27. Prometheus must scrape LiteLLM metrics.
28. Prometheus must scrape the custom platform exporter.
29. The custom platform exporter must expose `/metrics`.
30. The custom platform exporter must expose `/healthz`.
31. The exporter must report whether the LiteLLM endpoint is reachable.
32. The exporter must report whether the vLLM `/models` endpoint is reachable.
33. The exporter must report the active model name if `/models` succeeds.
34. The exporter must report current process RAM/CPU for the local machine if available.
35. The exporter must report tunnel health by checking the configured vLLM base URL.
36. The exporter must not crash if Slurm is unavailable locally.
37. If Slurm is unavailable, Slurm metrics must report `unknown` or `0` health state.
38. The exporter must support configuration through environment variables.
39. The docs must explain how to open Grafana.
40. The docs must explain default ports.

### 6.4 Benchmark foundation

41. Add a `benchmark/` folder.
42. Add benchmark case schema.
43. Add benchmark result schema.
44. Add at least one smoke benchmark case for RTL generation.
45. Add at least one smoke benchmark case for testbench generation.
46. Add a runner that can call LiteLLM using an OpenAI-compatible API.
47. The runner must store each model response.
48. The runner must extract code blocks from responses.
49. The runner must classify missing-code failures.
50. The runner must support timeout handling.
51. The runner must store benchmark results in PostgreSQL.
52. The runner must support a local JSON result output fallback.
53. The runner must record prompt version.
54. The runner must record model alias.
55. The runner must record request start time and end time.
56. The runner must record latency in milliseconds.
57. The runner must record input tokens when available.
58. The runner must record output tokens when available.
59. The runner must record total tokens when available.
60. The runner must record compile status.
61. The runner must record simulation status.
62. The runner must record failure category.
63. The runner must record generated artifacts.
64. The runner must support a `--dry-run` mode that validates cases without calling LiteLLM.
65. The runner must support a `--suite smoke` command.
66. The runner must support a `--model active-lanta-model` argument.
67. The runner must support a `--prompt-version` argument.
68. The runner must produce a nonzero exit code if any required case file is invalid.
69. The runner must not produce a nonzero exit code merely because a model fails a benchmark case, unless `--fail-on-benchmark-fail` is passed.

### 6.5 Benchmark dashboard backend

70. Add a dashboard backend service.
71. Backend must expose APIs for listing benchmark runs.
72. Backend must expose APIs for reading one benchmark run.
73. Backend must expose APIs for listing benchmark cases.
74. Backend must expose APIs for reading one benchmark case.
75. Backend must expose APIs for summary statistics.
76. Backend must return JSON.
77. Backend must validate IDs.
78. Backend must return 404 for missing resources.
79. Backend must not expose secrets.
80. Backend must support CORS only for configured local origins.

### 6.6 Documentation

81. Add:

```text
docs/specs/llm-platform-control-plane.md
```

82. Add or update:

```text
docs/ARCHITECTURE.md
docs/OPERATIONS.md
docs/BENCHMARKING.md
```

83. Update root `README.md` with the new platform architecture.
84. Existing `HOW_TO_USE.md` and `HOW_TO_SWAP.md` must remain valid.
85. Documentation must state the startup order:
86. Start Lanta vLLM job.
87. Start tunnel.
88. Start LiteLLM.
89. Start OpenWebUI.
90. Start observability stack.
91. Run benchmark suite.

## 7. Technical requirements

### 7.1 Target architecture

```text
User Browser
  |
  v
OpenWebUI
  |
  v
LiteLLM Proxy
  |
  v
Local SSH Tunnel
  |
  v
vLLM on Lanta Slurm
  |
  v
Active Hugging Face model
```

Monitoring path:

```text
LiteLLM /metrics
Platform exporter /metrics
Node/system exporters if available
  |
  v
Prometheus
  |
  v
Grafana
```

Benchmark path:

```text
Benchmark Runner
  |
  v
LiteLLM /v1/chat/completions
  |
  v
Generated response
  |
  v
Code extraction
  |
  v
Compile/simulate/check
  |
  v
PostgreSQL
  |
  v
Benchmark Dashboard API
```

### 7.2 Data flow

#### Chat flow

1. User sends message in OpenWebUI.
2. OpenWebUI sends OpenAI-compatible request to LiteLLM.
3. LiteLLM validates the key.
4. LiteLLM routes to `active-lanta-model`.
5. LiteLLM forwards to vLLM through the tunnel.
6. vLLM streams or returns completion.
7. LiteLLM logs usage and exposes metrics.
8. OpenWebUI stores the chat session in its own database.

#### API flow

1. User or script calls LiteLLM `/v1/chat/completions`.
2. User passes a LiteLLM virtual key.
3. LiteLLM validates access.
4. LiteLLM forwards to the active vLLM backend.
5. LiteLLM records usage.

#### Benchmark flow

1. User runs:

```bash
python -m benchmark.runners.run_suite --suite smoke --model active-lanta-model
```

2. Runner loads benchmark cases.
3. Runner builds prompt from case + prompt template.
4. Runner calls LiteLLM.
5. Runner saves raw response.
6. Runner extracts code block.
7. Runner runs compile evaluator if available.
8. Runner runs simulation evaluator if available.
9. Runner stores result in database.
10. Dashboard reads results from database.

### 7.3 Permissions and security

1. LiteLLM master key must never be committed.
2. OpenWebUI admin password must never be committed.
3. Grafana admin password must never be committed.
4. PostgreSQL password must never be committed.
5. `.env.example` may contain placeholder values only.
6. Generated API keys must not be printed into committed logs.
7. The old `sharing/` gateway may remain, but docs should mark LiteLLM as preferred.
8. CORS must default to local-only where practical.
9. OpenWebUI should not expose LiteLLM master key to normal users.
10. Benchmark artifacts may contain proprietary prompts or generated code, so docs must warn not to commit real benchmark results unless approved.
11. Add `.gitignore` entries for:

    * benchmark result artifacts
    * local database files
    * logs
    * generated secrets
    * Grafana local volume data
    * Prometheus local volume data

### 7.4 Validation rules

Benchmark case validation:

1. `id` is required and must match:

```regex
^[a-z0-9][a-z0-9_-]{2,80}$
```

2. `title` is required.
3. `task_type` must be one of:

   * `rtl_generation`
   * `testbench_generation`
   * `rtl_debugging`
   * `low_power_rewrite`
4. `prompt` is required.
5. `expected_language` must default to `systemverilog`.
6. `expected_module_name` is required for RTL generation cases.
7. `timeout_seconds` must be between `1` and `600`.
8. Evaluator config is optional but must be valid JSON/YAML if present.

Benchmark result validation:

1. `run_id` is required.
2. `case_id` is required.
3. `model_alias` is required.
4. `status` must be one of:

   * `passed`
   * `failed`
   * `error`
   * `skipped`
5. `failure_category` must be nullable or one of:

   * `none`
   * `no_code_block`
   * `wrong_module_name`
   * `missing_port`
   * `syntax_error`
   * `compile_error`
   * `simulation_mismatch`
   * `timeout`
   * `upstream_error`
   * `invalid_case`
   * `unknown`

## 8. Files likely involved

Create:

```text
docs/specs/llm-platform-control-plane.md
docs/ARCHITECTURE.md
docs/OPERATIONS.md
docs/BENCHMARKING.md

openwebui/
  docker-compose.yml
  .env.example
  README.md

litellm/
  docker-compose.yml
  config.yaml
  .env.example
  README.md

observability/
  docker-compose.yml
  README.md
  prometheus/
    prometheus.yml
  grafana/
    provisioning/
      datasources/
        prometheus.yml
      dashboards/
        dashboards.yml
    dashboards/
      lanta-llm-operations.json
  exporters/
    platform_exporter.py
    requirements.txt
    Dockerfile

benchmark/
  __init__.py
  cases/
    smoke/
      rtl_counter.yaml
      testbench_counter.yaml
  prompts/
    rfid_low_power_v1.md
    generic_sv_v1.md
  runners/
    __init__.py
    run_suite.py
  evaluators/
    __init__.py
    extract_code.py
    compile_sv.py
    simulate.py
    score.py
  schemas/
    case.schema.json
    result.schema.json
  storage/
    __init__.py
    db.py
    models.py
    migrations/
  artifacts/
    .gitkeep

dashboard/
  backend/
    app/
      main.py
      database.py
      routers/
        health.py
        benchmark_runs.py
        benchmark_cases.py
        summary.py
      schemas.py
    requirements.txt
    Dockerfile
  README.md
```

Modify:

```text
README.md
.gitignore
HOW_TO_USE.md
HOW_TO_SWAP.md
sharing/README.md if present
```

Do not delete:

```text
website/
sharing/
lanta/scripts/
windows/tunnel/
```

## 9. Data model

Use PostgreSQL.

### 9.1 Table: `benchmark_suites`

Fields:

```text
id UUID primary key
name TEXT not null unique
description TEXT nullable
created_at TIMESTAMPTZ not null default now()
updated_at TIMESTAMPTZ not null default now()
```

Indexes:

```text
unique(name)
```

### 9.2 Table: `benchmark_cases`

Fields:

```text
id TEXT primary key
suite_id UUID nullable references benchmark_suites(id)
title TEXT not null
task_type TEXT not null
description TEXT nullable
prompt TEXT not null
expected_language TEXT not null default 'systemverilog'
expected_module_name TEXT nullable
timeout_seconds INTEGER not null default 120
evaluator_config JSONB not null default '{}'
case_file_path TEXT nullable
created_at TIMESTAMPTZ not null default now()
updated_at TIMESTAMPTZ not null default now()
```

Indexes:

```text
index(task_type)
index(suite_id)
index(expected_module_name)
```

### 9.3 Table: `prompt_versions`

Fields:

```text
id UUID primary key
name TEXT not null unique
description TEXT nullable
content TEXT not null
content_sha256 TEXT not null
created_at TIMESTAMPTZ not null default now()
```

Indexes:

```text
unique(name)
unique(content_sha256)
```

### 9.4 Table: `benchmark_runs`

Fields:

```text
id UUID primary key
suite_name TEXT not null
model_alias TEXT not null
prompt_version TEXT not null
status TEXT not null
started_at TIMESTAMPTZ not null
finished_at TIMESTAMPTZ nullable
duration_ms INTEGER nullable
total_cases INTEGER not null default 0
passed_cases INTEGER not null default 0
failed_cases INTEGER not null default 0
error_cases INTEGER not null default 0
config JSONB not null default '{}'
created_by TEXT nullable
created_at TIMESTAMPTZ not null default now()
```

Allowed `status`:

```text
running
completed
failed
cancelled
```

Indexes:

```text
index(started_at)
index(model_alias)
index(prompt_version)
index(status)
```

### 9.5 Table: `benchmark_results`

Fields:

```text
id UUID primary key
run_id UUID not null references benchmark_runs(id) on delete cascade
case_id TEXT not null references benchmark_cases(id)
model_alias TEXT not null
prompt_version TEXT not null
status TEXT not null
failure_category TEXT nullable
failure_message TEXT nullable
request_started_at TIMESTAMPTZ nullable
request_finished_at TIMESTAMPTZ nullable
latency_ms INTEGER nullable
input_tokens INTEGER nullable
output_tokens INTEGER nullable
total_tokens INTEGER nullable
raw_response_path TEXT nullable
extracted_code_path TEXT nullable
compile_status TEXT nullable
compile_log_path TEXT nullable
simulation_status TEXT nullable
simulation_log_path TEXT nullable
score NUMERIC nullable
metadata JSONB not null default '{}'
created_at TIMESTAMPTZ not null default now()
```

Allowed `status`:

```text
passed
failed
error
skipped
```

Allowed `compile_status`:

```text
not_run
passed
failed
tool_missing
timeout
```

Allowed `simulation_status`:

```text
not_run
passed
failed
tool_missing
timeout
```

Indexes:

```text
index(run_id)
index(case_id)
index(model_alias)
index(prompt_version)
index(status)
index(failure_category)
```

### 9.6 Table: `platform_health_checks`

Fields:

```text
id UUID primary key
checked_at TIMESTAMPTZ not null default now()
component TEXT not null
status TEXT not null
latency_ms INTEGER nullable
message TEXT nullable
metadata JSONB not null default '{}'
```

Allowed `component`:

```text
litellm
vllm
ssh_tunnel
slurm
postgres
prometheus
grafana
```

Allowed `status`:

```text
ok
degraded
down
unknown
```

Indexes:

```text
index(checked_at)
index(component)
index(status)
```

### 9.7 Migration requirements

1. Provide SQL migrations or SQLAlchemy/Alembic migrations.
2. Migrations must be idempotent in local development.
3. The initial migration must create all benchmark tables.
4. The migration process must be documented in `docs/BENCHMARKING.md`.
5. No migration should delete existing user data.

## 10. API contract

### 10.1 Health check

Name: Dashboard Health
Method: `GET`
Path: `/api/healthz`

Request body:

```json
{}
```

Response body:

```json
{
  "ok": true,
  "service": "benchmark-dashboard",
  "database": "ok",
  "timestamp": "2026-06-14T00:00:00Z"
}
```

Error cases:

```json
{
  "ok": false,
  "service": "benchmark-dashboard",
  "database": "down",
  "error": "database connection failed"
}
```

Status codes:

```text
200 if healthy
503 if unhealthy
```

### 10.2 List benchmark runs

Name: List Benchmark Runs
Method: `GET`
Path: `/api/benchmark/runs`

Query params:

```text
limit optional integer default 50 max 200
offset optional integer default 0
model_alias optional string
prompt_version optional string
status optional string
suite_name optional string
```

Response body:

```json
{
  "items": [
    {
      "id": "uuid",
      "suite_name": "smoke",
      "model_alias": "active-lanta-model",
      "prompt_version": "rfid_low_power_v1",
      "status": "completed",
      "started_at": "2026-06-14T00:00:00Z",
      "finished_at": "2026-06-14T00:01:00Z",
      "duration_ms": 60000,
      "total_cases": 2,
      "passed_cases": 1,
      "failed_cases": 1,
      "error_cases": 0
    }
  ],
  "limit": 50,
  "offset": 0,
  "total": 1
}
```

Error cases:

```json
{
  "error": "invalid_query",
  "detail": "limit must be between 1 and 200"
}
```

Status codes:

```text
200 success
400 invalid query
500 database error
```

### 10.3 Get benchmark run detail

Name: Get Benchmark Run
Method: `GET`
Path: `/api/benchmark/runs/{run_id}`

Response body:

```json
{
  "id": "uuid",
  "suite_name": "smoke",
  "model_alias": "active-lanta-model",
  "prompt_version": "rfid_low_power_v1",
  "status": "completed",
  "started_at": "2026-06-14T00:00:00Z",
  "finished_at": "2026-06-14T00:01:00Z",
  "duration_ms": 60000,
  "total_cases": 2,
  "passed_cases": 1,
  "failed_cases": 1,
  "error_cases": 0,
  "results": [
    {
      "id": "uuid",
      "case_id": "rtl_counter",
      "status": "passed",
      "failure_category": null,
      "latency_ms": 12000,
      "input_tokens": 800,
      "output_tokens": 1200,
      "total_tokens": 2000,
      "compile_status": "passed",
      "simulation_status": "passed",
      "score": 1.0
    }
  ]
}
```

Error cases:

```json
{
  "error": "not_found",
  "detail": "benchmark run not found"
}
```

Status codes:

```text
200 success
404 missing run
500 database error
```

### 10.4 List benchmark cases

Name: List Benchmark Cases
Method: `GET`
Path: `/api/benchmark/cases`

Query params:

```text
suite_name optional string
task_type optional string
limit optional integer default 100 max 500
offset optional integer default 0
```

Response body:

```json
{
  "items": [
    {
      "id": "rtl_counter",
      "title": "Low-power enabled counter",
      "task_type": "rtl_generation",
      "expected_language": "systemverilog",
      "expected_module_name": "lp_counter",
      "timeout_seconds": 120
    }
  ],
  "limit": 100,
  "offset": 0,
  "total": 1
}
```

Error cases:

```json
{
  "error": "invalid_query",
  "detail": "unsupported task_type"
}
```

### 10.5 Get benchmark case

Name: Get Benchmark Case
Method: `GET`
Path: `/api/benchmark/cases/{case_id}`

Response body:

```json
{
  "id": "rtl_counter",
  "title": "Low-power enabled counter",
  "task_type": "rtl_generation",
  "description": "Generate a synthesizable low-power counter with enable.",
  "prompt": "Create a SystemVerilog module...",
  "expected_language": "systemverilog",
  "expected_module_name": "lp_counter",
  "timeout_seconds": 120,
  "evaluator_config": {},
  "latest_results": [
    {
      "run_id": "uuid",
      "model_alias": "active-lanta-model",
      "prompt_version": "rfid_low_power_v1",
      "status": "passed",
      "created_at": "2026-06-14T00:00:00Z"
    }
  ]
}
```

Error cases:

```json
{
  "error": "not_found",
  "detail": "benchmark case not found"
}
```

### 10.6 Summary statistics

Name: Benchmark Summary
Method: `GET`
Path: `/api/benchmark/summary`

Query params:

```text
since optional ISO datetime
model_alias optional string
prompt_version optional string
suite_name optional string
```

Response body:

```json
{
  "total_runs": 10,
  "total_results": 100,
  "pass_rate": 0.72,
  "compile_pass_rate": 0.81,
  "simulation_pass_rate": 0.64,
  "average_latency_ms": 15500,
  "average_total_tokens": 2400,
  "by_model": [
    {
      "model_alias": "active-lanta-model",
      "total_results": 100,
      "pass_rate": 0.72,
      "compile_pass_rate": 0.81,
      "simulation_pass_rate": 0.64
    }
  ],
  "failure_categories": [
    {
      "failure_category": "syntax_error",
      "count": 8
    }
  ]
}
```

Error cases:

```json
{
  "error": "invalid_query",
  "detail": "since must be an ISO datetime"
}
```

### 10.7 Artifact access

Name: Get Benchmark Artifact
Method: `GET`
Path: `/api/benchmark/artifacts/{result_id}/{artifact_type}`

Allowed `artifact_type`:

```text
raw_response
extracted_code
compile_log
simulation_log
```

Response body:

```json
{
  "result_id": "uuid",
  "artifact_type": "extracted_code",
  "content_type": "text/plain",
  "content": "module lp_counter (...); endmodule"
}
```

Error cases:

```json
{
  "error": "not_found",
  "detail": "artifact not found"
}
```

Security requirement:

* Do not allow arbitrary file paths.
* Resolve artifacts only from database paths under the configured artifact root.
* Reject path traversal attempts.

## 11. Edge cases

1. vLLM tunnel is down.
2. LiteLLM is up but vLLM is unreachable.
3. OpenWebUI is up but LiteLLM is down.
4. `/models` endpoint fails even though `/chat/completions` works.
5. Active model name changes after a Slurm swap.
6. Model swap happens during benchmark run.
7. LiteLLM returns no token usage.
8. LiteLLM streams a response but connection drops mid-stream.
9. Model returns no code block.
10. Model returns multiple code blocks.
11. Model returns Verilog instead of SystemVerilog.
12. Model uses wrong module name.
13. Model response is too long.
14. Benchmark case YAML is invalid.
15. Benchmark case references missing files.
16. Compile tool is not installed.
17. Simulation tool is not installed.
18. Compile times out.
19. Simulation times out.
20. PostgreSQL is unavailable.
21. Prometheus starts before LiteLLM.
22. Grafana starts before Prometheus.
23. Platform exporter cannot call Slurm commands on Windows.
24. GPU exporter is unavailable locally.
25. User commits local `.env` accidentally. Add `.gitignore` protection.
26. API key is invalid.
27. API key is valid but has no model access.
28. Request exceeds configured rate limit.
29. User sends concurrent benchmark runs.
30. Benchmark artifact file is missing but database row exists.

## 12. Testing plan

### 12.1 Unit tests

Add tests for:

1. Benchmark case schema validation.
2. Result schema validation.
3. Code block extraction.
4. Failure category classification.
5. Artifact path safety.
6. LiteLLM client request construction.
7. Token usage parsing.
8. Summary statistics calculation.
9. Platform exporter metric formatting.
10. Health check status mapping.

Example test cases:

```text
extract_code should return first SystemVerilog code block
extract_code should return largest code block if no language tag exists
extract_code should classify empty response as no_code_block
artifact resolver should reject ../../secret.txt
case validator should reject invalid task_type
```

### 12.2 Integration tests

Add integration tests for:

1. Dashboard API starts and returns `/api/healthz`.
2. Benchmark run can be inserted and listed.
3. Benchmark run detail returns child results.
4. Summary endpoint returns expected aggregate values.
5. Platform exporter returns Prometheus text format.
6. LiteLLM config file exists and contains `active-lanta-model`.
7. Docker Compose config validates for OpenWebUI.
8. Docker Compose config validates for LiteLLM.
9. Docker Compose config validates for observability.

### 12.3 UI tests

Minimum manual or automated UI checks:

1. Open benchmark overview page with no data.
2. Open benchmark overview page with seeded data.
3. Open benchmark runs page.
4. Open benchmark run detail page.
5. Open benchmark case detail page.
6. Verify long logs do not break layout.
7. Verify missing artifacts show a clear error message.

### 12.4 Manual checks

Manual startup check:

```bash
docker compose -f litellm/docker-compose.yml up -d
docker compose -f openwebui/docker-compose.yml up -d
docker compose -f observability/docker-compose.yml up -d
```

Manual LiteLLM check:

```bash
curl http://127.0.0.1:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

Manual chat completion check:

```bash
curl http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "active-lanta-model",
    "messages": [
      {"role": "user", "content": "Reply exactly: online"}
    ],
    "temperature": 0,
    "max_tokens": 8
  }'
```

Manual metrics check:

```bash
curl http://127.0.0.1:4000/metrics
curl http://127.0.0.1:9108/metrics
```

Manual benchmark dry run:

```bash
python -m benchmark.runners.run_suite --suite smoke --dry-run
```

Manual benchmark run:

```bash
python -m benchmark.runners.run_suite \
  --suite smoke \
  --model active-lanta-model \
  --prompt-version rfid_low_power_v1
```

Manual dashboard check:

```bash
curl http://127.0.0.1:8088/api/healthz
curl http://127.0.0.1:8088/api/benchmark/runs
curl http://127.0.0.1:8088/api/benchmark/summary
```

### 12.5 Lint/typecheck

Run applicable checks based on implementation language:

```bash
python -m compileall benchmark dashboard observability
python -m pytest
```

If Node files are modified:

```bash
cd website
npm run check
```

If Docker Compose is installed:

```bash
docker compose -f litellm/docker-compose.yml config
docker compose -f openwebui/docker-compose.yml config
docker compose -f observability/docker-compose.yml config
```

## 13. Definition of done

The task is complete only when:

* All functional requirements are implemented.
* Tests pass.
* Lint/typecheck passes.
* Existing behavior is not broken.
* The implementation matches this spec.
* OpenWebUI can be configured to talk to LiteLLM.
* LiteLLM can proxy to the existing vLLM endpoint.
* Prometheus can scrape LiteLLM and the platform exporter.
* Grafana has at least one provisioned LLM operations dashboard.
* Benchmark smoke cases exist.
* Benchmark runner supports dry-run mode.
* Benchmark runner can call LiteLLM.
* Benchmark results can be stored.
* Benchmark dashboard API can list runs, cases, summaries, and artifacts.
* Documentation explains startup, operations, API keys, monitoring, and benchmarking.
* Secrets are not committed.
* Existing `website/`, `sharing/`, `lanta/scripts/`, and `windows/tunnel/` flows remain usable.

## 14. Codex implementation instructions

Implement this spec.

Use the existing repository patterns and do not rewrite unrelated parts of the project.

Do not delete the existing custom `website/` UI. Keep it as a fallback demo UI.

Do not delete the existing `sharing/` gateway. Add documentation saying LiteLLM is now the preferred API gateway, but keep the old gateway for compatibility.

Do not change existing Lanta Slurm behavior unless required for integration. The first version should assume one active model on port `8000`.

Create the spec file at:

```text
docs/specs/llm-platform-control-plane.md
```

Then implement the required folders and files:

```text
openwebui/
litellm/
observability/
benchmark/
dashboard/
docs/
```

Do not introduce new dependencies unless necessary. If a dependency is necessary, document why it is needed.

Prefer simple, maintainable implementation over clever abstractions.

Use environment variables for all secrets and configurable endpoints.

Add `.env.example` files, but never commit real secrets.

Add `.gitignore` entries for generated results, local metrics data, database volumes, logs, and secrets.

Follow these defaults unless the repo already defines alternatives:

```text
LiteLLM port: 4000
OpenWebUI port: 3000
Grafana port: 3002
Prometheus port: 9090
Platform exporter port: 9108
Benchmark dashboard API port: 8088
vLLM tunnel URL: http://127.0.0.1:8000/v1
LiteLLM model alias: active-lanta-model
```

Run relevant checks before finishing:

```bash
python -m compileall benchmark dashboard observability
python -m pytest
docker compose -f litellm/docker-compose.yml config
docker compose -f openwebui/docker-compose.yml config
docker compose -f observability/docker-compose.yml config
```

If tests cannot be run in the current environment, clearly state which tests could not be run and why.

At the end, summarize:

1. Files created.
2. Files modified.
3. How to start the new stack.
4. How to verify OpenWebUI to LiteLLM to vLLM.
5. How to view Grafana.
6. How to run the smoke benchmark.
7. Any tradeoffs or incomplete pieces.