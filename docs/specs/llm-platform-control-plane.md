# Feature Spec: LLM Platform Control Plane - Phase 2 Operations, Model Sync, and Evaluation Maturity

## 1. Goal

The first foundation of the Lanta LLM platform is now in place. The repository has OpenWebUI, LiteLLM, observability, benchmark, dashboard, and platform check tooling. The next milestone is to make the platform easier to operate daily, more transparent to admins, and more useful for comparing HDL-capable local LLMs.

Phase 2 should focus on five outcomes:

1. **Reliable model identity and swap workflow**: when the active vLLM model changes on Lanta, local services should detect it, update the LiteLLM upstream model routing, and clearly show the real model name to admins.
2. **Better observability**: Grafana should distinguish between local/container health, LiteLLM usage, vLLM tunnel health, and real Lanta GPU/Slurm state. GPU panels should be backed by real metrics, not placeholders.
3. **Admin status visibility**: add a simple platform status view/API that shows the public model alias, real upstream vLLM model, tunnel health, LiteLLM health, OpenWebUI health, benchmark dashboard health, and observability health.
4. **Benchmark maturity**: expand benchmark cases beyond smoke tests, improve scoring metadata, store both model alias and resolved upstream model, and make benchmark results easier to compare across model swaps.
5. **Operations polish**: make startup, health checks, model swapping, and troubleshooting simple enough that a new intern or engineer can run the stack without guessing.

The current intended architecture remains:

```text
OpenWebUI -> LiteLLM -> local SSH tunnel -> vLLM on Lanta
```

The current stable public LiteLLM alias remains:

```text
active-lanta-model
```

The real upstream model is controlled by:

```text
VLLM_MODEL_ID=openai/<model-id-returned-by-vllm>
```

Phase 2 must preserve the stable alias for scripts and users, while making the real model name visible and easy to synchronize.

## 2. Current state snapshot

This section documents the current repository state before Phase 2.

### 2.1 Already implemented

The repository already has these major components:

```text
litellm/              LiteLLM gateway, config, Docker Compose, .env example, README
openwebui/            OpenWebUI Docker Compose and .env example
observability/        Prometheus, Grafana, platform exporter, dashboard JSON
benchmark/            HDL benchmark runner, cases, evaluators, storage, artifacts
dashboard/            FastAPI benchmark dashboard/API
scripts/check-platform.ps1
                      Local health checker for vLLM, LiteLLM, OpenWebUI, exporter, dashboard
```

### 2.2 Current chat flow

```text
User Browser
  |
  v
OpenWebUI on http://127.0.0.1:3000
  |
  v
LiteLLM on http://127.0.0.1:4000/v1
  |
  v
host.docker.internal:8000/v1
  |
  v
Windows SSH tunnel
  |
  v
vLLM running on Lanta Slurm
```

### 2.3 Current model routing

LiteLLM exposes a stable public model name:

```text
active-lanta-model
```

LiteLLM forwards that alias to the model configured by:

```text
VLLM_MODEL_ID
```

Example:

```env
VLLM_MODEL_ID=openai/qwen36-35b-a3b
```

This means the user or benchmark can always call:

```text
active-lanta-model
```

while the admin can change the real model behind it.

### 2.4 Current observability

Prometheus currently scrapes:

```text
litellm:4000/metrics
platform-exporter:9108/metrics
```

The current Grafana dashboard already has panels for:

1. Current active model.
2. LiteLLM request rate.
3. In-flight requests if LiteLLM exposes the metric.
4. Total requests.
5. Error rate.
6. p50 and p95 latency.
7. Input/output tokens per minute.
8. Output token/s from LiteLLM metrics.
9. Usage by API key/user.
10. Usage by model alias.
11. vLLM upstream health.
12. SSH tunnel health.
13. Local/container CPU/RAM/disk.
14. Slurm job state if `squeue` is available.
15. GPU panels using DCGM metric names, but without a real GPU exporter yet.

### 2.5 Known gaps

Phase 2 should address these gaps:

1. Model swap is still manual after `submit-preset.sh`; `VLLM_MODEL_ID` must be updated and LiteLLM must be recreated.
2. OpenWebUI shows `active-lanta-model`, not the true underlying vLLM model.
3. There is no status page showing both public alias and real model.
4. GPU panels exist but do not receive real Lanta GPU metrics.
5. Slurm panels may not work from the local Docker exporter because the local container usually cannot run Lanta `squeue`.
6. Benchmark results store the model alias, but not always the resolved upstream model at run time.
7. Benchmark suite is still small and should grow toward RFID/digital IC workflows.
8. There is no one-command model-sync tool.
9. There is no one-command full stack startup script.
10. OpenWebUI persistent provider settings can confuse users after `.env` changes.

## 3. Non-goals

Phase 2 should **not** build:

1. A full public SaaS product.
2. Billing or customer payment flows.
3. Enterprise SSO or complex RBAC.
4. A new chat UI replacing OpenWebUI.
5. Full RTL synthesis, place-and-route, or accurate silicon area/power signoff.
6. A new Slurm scheduler.
7. A fully distributed Kubernetes platform.
8. Automatic GPU exporter deployment requiring root/admin privileges on Lanta unless documented as optional.
9. Destructive reset scripts that delete user data by default.
10. A benchmark leaderboard claiming scientific validity without clear methodology and limitations.

The existing `website/`, `sharing/`, `lanta/scripts/`, and `windows/tunnel/` folders must remain available.

## 4. Assumptions

1. The repository remains `ArmmyC/Lanta-LLM-Hosting`.
2. The main local vLLM tunnel remains:

```text
http://127.0.0.1:8000/v1
```

3. Docker containers reach the local tunnel through:

```text
http://host.docker.internal:8000/v1
```

4. Only one vLLM model is served on port `8000` at a time in the current Lanta setup.
5. Model swapping on Lanta still cancels the previous `vllm-model` Slurm job and starts another job on the same endpoint.
6. OpenWebUI remains the main chat UI.
7. LiteLLM remains the central API gateway.
8. `active-lanta-model` remains the stable public model alias unless explicitly changed.
9. Admins should see the real upstream model name somewhere clear, even if users keep using the stable alias.
10. Prometheus and Grafana remain the monitoring stack.
11. Benchmark dashboard remains separate from OpenWebUI.
12. Benchmark local JSON storage remains acceptable for development.
13. PostgreSQL remains the desired long-term storage for LiteLLM and benchmark metadata.
14. `.env` files are local-only and must never be committed.
15. The implementation should prefer clear PowerShell scripts for Windows local operations.

## 5. User stories

### 5.1 Engineer using chat

* As an engineer, I want to open OpenWebUI and chat with the active Lanta model without knowing Slurm commands.
* As an engineer, I want the UI or status page to tell me what real model is active, so I know whether I am using Qwen, DeepSeek, or another model.
* As an engineer, I want model swaps to be reflected quickly, so I do not accidentally test the wrong model.

### 5.2 Admin operating the stack

* As an admin, I want to run one health check command and know whether vLLM, LiteLLM, OpenWebUI, observability, and dashboard are healthy.
* As an admin, I want to run one model-sync command after swapping models on Lanta.
* As an admin, I want a platform status page showing public alias, real upstream model, LiteLLM health, vLLM health, tunnel health, and last sync time.
* As an admin, I want Grafana to show which panels are real and which require optional exporters.
* As an admin, I want to see token usage and token/s from LiteLLM.
* As an admin, I want real Lanta GPU usage if a Lanta-side exporter is enabled.

### 5.3 Benchmark maintainer

* As a benchmark maintainer, I want each benchmark run to record both `model_alias` and `resolved_upstream_model`, so results remain understandable after model swaps.
* As a benchmark maintainer, I want more cases for RTL generation, testbench generation, debugging, and low-power rewrite tasks.
* As a benchmark maintainer, I want failure categories that help me improve prompts and model choice.
* As a benchmark maintainer, I want benchmark results visible in the dashboard without opening raw JSON files.

### 5.4 Developer extending the repo

* As a developer, I want clear docs explaining the flow and ownership of each component.
* As a developer, I want scripts to fail safely and print actionable next steps.
* As a developer, I want tests covering model sync, status APIs, benchmark scoring, and artifact path safety.

## 6. UX / UI requirements

### 6.1 OpenWebUI experience

OpenWebUI remains the primary chat UI.

Required behavior:

1. Users open:

```text
http://127.0.0.1:3000
```

2. Users log in with OpenWebUI accounts.
3. Users select a model exposed by LiteLLM.
4. Users chat normally.
5. OpenWebUI sends requests to LiteLLM, not directly to vLLM.
6. OpenWebUI may continue to show `active-lanta-model` as the selectable model.
7. A clear admin-facing status page must show the true upstream model.
8. Docs must explain that OpenWebUI account login is separate from LiteLLM API keys.

Recommended behavior:

1. Keep `active-lanta-model` for user-facing stability.
2. Do not force OpenWebUI to rename the model after every swap unless this can be done safely.
3. Show the real active model in dashboard/Grafana/status page instead.
4. Add docs explaining why stable alias is preferred for scripts and benchmarks.

### 6.2 Model identity display

The platform must expose three names clearly:

```text
public_alias: active-lanta-model
litellm_model_id: openai/<real-vllm-model>
vllm_reported_model_id: <model-returned-by-/v1/models>
```

Example:

```json
{
  "public_alias": "active-lanta-model",
  "litellm_model_id": "openai/qwen36-35b-a3b",
  "vllm_reported_model_id": "qwen36-35b-a3b"
}
```

This information should appear in at least one of:

1. Benchmark dashboard status page.
2. Grafana current active model panel.
3. `scripts/check-platform.ps1` output.
4. New `scripts/sync-active-model.ps1` output.

### 6.3 Model swap experience

Desired admin flow:

```powershell
ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/submit-preset.sh qwen36-35b-a3b"

powershell -ExecutionPolicy Bypass -File .\scripts\sync-active-model.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\check-platform.ps1
```

`sync-active-model.ps1` should:

1. Call `http://127.0.0.1:8000/v1/models`.
2. Extract the current vLLM model id.
3. Convert it to LiteLLM format by prefixing `openai/` unless already prefixed.
4. Update `litellm/.env` value:

```env
VLLM_MODEL_ID=openai/<model-id>
```

5. Recreate the LiteLLM service by default or offer a `-NoRestart` flag.
6. Print what changed.
7. Never print secrets.
8. Warn if OpenWebUI may need model refresh.

### 6.4 Platform status page

Add a lightweight status view to the dashboard backend.

Minimum page:

```text
http://127.0.0.1:8088/status
```

Minimum API:

```text
GET /api/platform/status
```

Displayed fields:

1. Public model alias.
2. LiteLLM configured upstream model id.
3. vLLM reported model id.
4. LiteLLM health.
5. vLLM tunnel health.
6. OpenWebUI health.
7. Platform exporter health.
8. Prometheus health if reachable.
9. Grafana health if reachable.
10. Benchmark dashboard health.
11. Last successful health check timestamp.
12. Suggested fix if a component is down.

### 6.5 Grafana operations dashboard

Keep dashboard name:

```text
Lanta LLM Operations
```

Required rows:

1. Inference.
2. Usage.
3. Local Platform.
4. Lanta/Slurm.
5. GPU if available.
6. Benchmark.

Required panel behavior:

1. Token/s must be labeled as LiteLLM-observed token/s.
2. GPU panels must clearly say when no GPU exporter is configured.
3. Slurm panels must clearly say when Slurm cannot be checked from local Docker.
4. Current active model must show the vLLM-reported model label.
5. Model alias usage should show `active-lanta-model` separately from the resolved upstream model when possible.

## 7. Functional requirements

### 7.1 Model sync script

Add:

```text
scripts/sync-active-model.ps1
```

Required options:

```powershell
.\scripts\sync-active-model.ps1
.\scripts\sync-active-model.ps1 -NoRestart
.\scripts\sync-active-model.ps1 -ExpectedModel qwen36-35b-a3b
.\scripts\sync-active-model.ps1 -LiteLLMEnvPath .\litellm\.env
```

Required behavior:

1. Read vLLM models from:

```text
http://127.0.0.1:8000/v1/models
```

2. If no model is returned, fail with a clear message.
3. If multiple models are returned, choose the first by default and print a warning.
4. Normalize the model for LiteLLM:

```text
qwen36-35b-a3b -> openai/qwen36-35b-a3b
openai/qwen36-35b-a3b -> openai/qwen36-35b-a3b
```

5. Create `litellm/.env` from `.env.example` if missing, but ask the user to fill secrets if required.
6. Update only the `VLLM_MODEL_ID` line.
7. Preserve all other `.env` values and comments as much as practical.
8. Print old model and new model.
9. Recreate LiteLLM unless `-NoRestart` is used:

```powershell
cd .\litellm
docker compose up -d --force-recreate litellm
```

10. Re-run basic LiteLLM health check after restart.
11. Exit nonzero on failure.

### 7.2 Platform check script improvements

Update:

```text
scripts/check-platform.ps1
```

Add checks for:

1. Current vLLM model id from `/v1/models`.
2. Current `VLLM_MODEL_ID` from `litellm/.env`.
3. Whether `VLLM_MODEL_ID` matches the vLLM reported model after removing `openai/` prefix.
4. LiteLLM `/v1/models` includes `active-lanta-model`.
5. LiteLLM `/metrics` is reachable.
6. Prometheus `/-/ready` is reachable.
7. Grafana `/api/health` is reachable.
8. Dashboard `/api/platform/status` is reachable after that endpoint is implemented.

Output format:

```text
PASS vLLM tunnel - HTTP 200, model=qwen36-35b-a3b
PASS LiteLLM health - HTTP 200
PASS LiteLLM model alias - active-lanta-model available
PASS Model sync - VLLM_MODEL_ID=openai/qwen36-35b-a3b matches vLLM=qwen36-35b-a3b
WARN GPU metrics - no DCGM exporter configured
FAIL OpenWebUI homepage - connection refused
```

Rules:

1. Do not print API keys.
2. Print commands users can run to fix common problems.
3. Use exit code `0` if all required checks pass.
4. Use exit code `1` if required checks fail.
5. Warnings should not fail the script unless `-Strict` is passed.

### 7.3 LiteLLM configuration

Keep:

```text
active-lanta-model
```

as the stable public alias.

Keep `VLLM_MODEL_ID` in `litellm/.env.example`.

Required behavior:

1. `litellm/config.yaml` must use `os.environ/VLLM_MODEL_ID`.
2. `litellm/README.md` must explain:
   * public alias
   * resolved upstream model
   * how to change model
   * how to sync automatically
   * why OpenWebUI may continue showing the stable alias
3. `litellm/docker-compose.yml` must pass `VLLM_MODEL_ID` into the container.
4. Do not commit real `.env` files.

Optional enhancement:

Support a second visible model alias for the real model name, but only if it does not break existing benchmark commands or virtual key restrictions.

Example optional config:

```yaml
model_list:
  - model_name: active-lanta-model
    litellm_params:
      model: os.environ/VLLM_MODEL_ID
      api_base: os.environ/VLLM_BASE_URL
      api_key: os.environ/VLLM_API_KEY
```

If exposing the real model name as a second alias is implemented, document tradeoffs clearly.

### 7.4 OpenWebUI behavior

Do not make OpenWebUI directly call vLLM.

OpenWebUI should continue using:

```text
http://litellm:4000/v1
```

Requirements:

1. `openwebui/.env.example` must remain simple.
2. Docs must explain first admin account creation.
3. Docs must explain that OpenWebUI settings may persist after first launch.
4. Docs must explain how to refresh or manually update the provider if `.env` changes are not reflected.
5. Do not recommend deleting the OpenWebUI volume unless the user accepts losing chat/users/settings.

### 7.5 Lanta-side observability exporter

Add an optional Lanta-side exporter or script.

Preferred path:

```text
lanta/scripts/lanta-metrics-exporter.py
```

Alternative acceptable path:

```text
observability/exporters/lanta_gpu_exporter.py
```

Required metrics:

```text
lanta_gpu_available
lanta_gpu_utilization_percent
lanta_gpu_memory_used_bytes
lanta_gpu_memory_total_bytes
lanta_gpu_power_watts
lanta_gpu_temperature_celsius
lanta_vllm_process_running
lanta_vllm_process_gpu_memory_bytes
lanta_slurm_job_running
lanta_slurm_job_state
lanta_slurm_job_runtime_seconds
```

Implementation options:

1. Parse `nvidia-smi --query-gpu=... --format=csv,noheader,nounits`.
2. Parse `squeue` for job state.
3. Optionally parse `ps` for vLLM process.
4. Expose `/metrics` over HTTP on a configurable port.
5. Expose `/healthz`.

Security constraints:

1. Bind to localhost by default on Lanta.
2. Do not expose publicly by default.
3. Document SSH tunnel instructions if local Prometheus should scrape it.
4. Do not require root privileges.
5. If `nvidia-smi` is unavailable, export `lanta_gpu_available 0` and do not crash.

### 7.6 Prometheus/Grafana upgrades

Update Prometheus config to optionally scrape Lanta exporter.

Example target through a local tunnel:

```yaml
- job_name: lanta-gpu-exporter
  metrics_path: /metrics
  static_configs:
    - targets:
        - host.docker.internal:9208
```

Grafana requirements:

1. Keep existing panels for LiteLLM metrics.
2. Add row title: `GPU / Lanta Node`.
3. Add GPU utilization time series.
4. Add GPU memory used/total.
5. Add GPU power draw.
6. Add GPU temperature.
7. Add vLLM process running stat.
8. Add Slurm job runtime stat.
9. If metrics are missing, show a text panel explaining how to enable Lanta exporter.
10. Label LiteLLM token/s as gateway-observed token/s.

### 7.7 Benchmark runner improvements

Update benchmark results to record resolved model identity.

Add fields to result metadata or schema:

```text
public_model_alias
resolved_upstream_model
vllm_reported_model
litellm_base_url
vllm_base_url
```

Requirements:

1. Before each benchmark run, call vLLM `/models` if reachable.
2. Store the reported model id in run config or result metadata.
3. Store `VLLM_MODEL_ID` if available.
4. Store LiteLLM alias used by the request.
5. Dashboard should display both alias and resolved model.
6. If model changes during a run, mark run metadata with a warning.

Add CLI option:

```bash
python -m benchmark.runners.run_suite --suite smoke --model active-lanta-model --record-platform-status
```

Default should be to record platform status if safe and fast.

### 7.8 Benchmark case expansion

Add a new suite:

```text
benchmark/cases/rfid_basic/
```

Minimum new cases:

1. `edge_detector.yaml`
   * RTL generation
   * expected module: `edge_detector`
   * checks reset, input synchronization, pulse output
2. `clock_enable_counter.yaml`
   * RTL generation
   * low dynamic power focus
   * checks enable behavior and no unnecessary toggling in code structure
3. `spi_register_bank.yaml`
   * RTL generation
   * simple bus/register interface
4. `uart_rx_debug.yaml`
   * RTL debugging task with broken code input
5. `rfid_crc16.yaml`
   * RTL generation or debug
   * checks deterministic combinational/sequential CRC behavior
6. `testbench_edge_detector.yaml`
   * testbench generation
   * auxiliary DUT fixture
   * requires `PASS` output
7. `low_power_rewrite_counter.yaml`
   * low-power rewrite task
   * asks model to reduce toggling while preserving behavior

Each case must include:

```yaml
id:
title:
task_type:
description:
prompt:
expected_language: systemverilog
expected_module_name:
timeout_seconds:
evaluator_config:
  required_terms: []
  expected_pass_text: PASS
  forbidden_fail_text: FAIL
```

Use auxiliary fixtures where needed.

### 7.9 Benchmark scoring improvements

Keep the current simple evaluator, but add better metadata.

Failure categories should include:

```text
none
no_code_block
wrong_module_name
missing_required_term
compile_error
simulation_mismatch
timeout
upstream_error
invalid_case
tool_missing
unknown
```

Do not use `missing_port` for general required terms.

Scoring levels:

```text
1.0 = passed static + compile + simulation where applicable
0.7 = static passed and compile tool missing
0.5 = static passed but simulation unavailable
0.0 = failed/error
```

If keeping binary score for now, document that it is binary and add score metadata for future expansion.

### 7.10 Dashboard status and benchmark UI

Add platform status endpoint:

```text
GET /api/platform/status
```

Add simple HTML page:

```text
/status
```

Add benchmark pages or improve existing pages to show:

1. Latest run.
2. Pass rate by real model.
3. Pass rate by public alias.
4. Compile pass rate.
5. Simulation pass rate.
6. Failure category distribution.
7. Average latency.
8. Average output tokens.
9. Average output token/s if available.
10. Artifact links.

### 7.11 Operations docs

Update:

```text
docs/OPERATIONS.md
docs/BENCHMARKING.md
docs/ARCHITECTURE.md
README.md
HOW_TO_SWAP.md
```

Docs must explain:

1. First local run.
2. Startup order.
3. `.env` file purpose for each service.
4. Stable alias vs real upstream model.
5. Running `sync-active-model.ps1` after model swap.
6. Running `check-platform.ps1` after startup.
7. Enabling optional Lanta GPU exporter.
8. Difference between LiteLLM metrics and true GPU metrics.
9. OpenWebUI admin account creation.
10. Troubleshooting `curl: (52) Empty reply from server`.
11. Troubleshooting wrong model name.
12. Troubleshooting Docker not picking up `.env` changes.
13. Safe local reset using `docker compose down -v` only when data loss is acceptable.

## 8. Technical architecture

### 8.1 Current architecture

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
vLLM on Lanta
```

### 8.2 Phase 2 target architecture

```text
User Browser
  |
  v
OpenWebUI
  |
  v
LiteLLM Proxy  <----------------------+
  |                                    |
  v                                    |
Local SSH Tunnel                       |
  |                                    |
  v                                    |
vLLM on Lanta                         |
  |                                    |
  v                                    |
Active Hugging Face Model             |
                                       |
Model Sync Script ---------------------+
  |
  v
litellm/.env VLLM_MODEL_ID
```

Observability path:

```text
LiteLLM /metrics ---------------------+
Platform exporter /metrics ----------+--> Prometheus --> Grafana
Optional Lanta exporter /metrics -----+
```

Dashboard/status path:

```text
Dashboard backend
  |
  +--> reads benchmark results
  +--> checks LiteLLM/vLLM/OpenWebUI/exporter health
  +--> exposes /api/platform/status
  +--> serves /status
```

### 8.3 Model identity rules

Definitions:

```text
public_alias = model name users/scripts call through LiteLLM
litellm_model_id = provider-prefixed model sent by LiteLLM to vLLM
vllm_reported_model_id = model id returned by vLLM /v1/models
```

Example:

```text
public_alias = active-lanta-model
litellm_model_id = openai/qwen36-35b-a3b
vllm_reported_model_id = qwen36-35b-a3b
```

Rules:

1. `public_alias` should remain stable.
2. `litellm_model_id` should be updated after model swaps.
3. `vllm_reported_model_id` is the source of truth for what is actually running.
4. Health checks should warn if `litellm_model_id` suffix does not match `vllm_reported_model_id`.
5. Benchmarks should record all three when possible.

## 9. Data model additions

### 9.1 Benchmark run metadata

Add to `benchmark_runs.config` or equivalent structured metadata:

```json
{
  "public_model_alias": "active-lanta-model",
  "resolved_upstream_model": "openai/qwen36-35b-a3b",
  "vllm_reported_model": "qwen36-35b-a3b",
  "litellm_base_url": "http://127.0.0.1:4000/v1",
  "vllm_base_url": "http://127.0.0.1:8000/v1",
  "platform_status_checked_at": "2026-06-14T00:00:00Z",
  "model_sync_warning": null
}
```

### 9.2 Platform status response model

Define a status object:

```json
{
  "timestamp": "2026-06-14T00:00:00Z",
  "overall_status": "ok",
  "model": {
    "public_alias": "active-lanta-model",
    "litellm_model_id": "openai/qwen36-35b-a3b",
    "vllm_reported_model_id": "qwen36-35b-a3b",
    "model_sync_status": "ok"
  },
  "components": {
    "litellm": { "status": "ok", "latency_ms": 25, "message": "ok" },
    "vllm": { "status": "ok", "latency_ms": 40, "message": "ok" },
    "openwebui": { "status": "ok", "latency_ms": 30, "message": "ok" },
    "platform_exporter": { "status": "ok", "latency_ms": 5, "message": "ok" },
    "prometheus": { "status": "ok", "latency_ms": 12, "message": "ok" },
    "grafana": { "status": "ok", "latency_ms": 20, "message": "ok" },
    "dashboard": { "status": "ok", "latency_ms": 5, "message": "ok" }
  },
  "warnings": []
}
```

Allowed component status:

```text
ok
degraded
down
unknown
```

Allowed overall status:

```text
ok
degraded
down
unknown
```

### 9.3 Lanta exporter metrics

Use Prometheus text format.

Required metric examples:

```text
lanta_gpu_available 1
lanta_gpu_utilization_percent{gpu="0",name="NVIDIA H100"} 72
lanta_gpu_memory_used_bytes{gpu="0"} 42362470400
lanta_gpu_memory_total_bytes{gpu="0"} 84934656000
lanta_gpu_power_watts{gpu="0"} 512
lanta_gpu_temperature_celsius{gpu="0"} 66
lanta_vllm_process_running 1
lanta_slurm_job_running{job_id="123456",state="RUNNING",node="gpu-node-1"} 1
lanta_slurm_job_runtime_seconds{job_id="123456"} 3600
```

## 10. API contract

### 10.1 Platform status

Name: Platform Status

Method:

```text
GET
```

Path:

```text
/api/platform/status
```

Query params:

```text
include_details optional boolean default true
```

Success response:

```json
{
  "timestamp": "2026-06-14T00:00:00Z",
  "overall_status": "ok",
  "model": {
    "public_alias": "active-lanta-model",
    "litellm_model_id": "openai/qwen36-35b-a3b",
    "vllm_reported_model_id": "qwen36-35b-a3b",
    "model_sync_status": "ok"
  },
  "components": {
    "litellm": { "status": "ok", "latency_ms": 25, "message": "ok" },
    "vllm": { "status": "ok", "latency_ms": 40, "message": "ok" },
    "openwebui": { "status": "ok", "latency_ms": 30, "message": "ok" },
    "platform_exporter": { "status": "ok", "latency_ms": 5, "message": "ok" },
    "prometheus": { "status": "ok", "latency_ms": 12, "message": "ok" },
    "grafana": { "status": "ok", "latency_ms": 20, "message": "ok" },
    "dashboard": { "status": "ok", "latency_ms": 5, "message": "ok" }
  },
  "warnings": []
}
```

Degraded response example:

```json
{
  "timestamp": "2026-06-14T00:00:00Z",
  "overall_status": "degraded",
  "model": {
    "public_alias": "active-lanta-model",
    "litellm_model_id": "openai/qwen36-27b",
    "vllm_reported_model_id": "qwen36-35b-a3b",
    "model_sync_status": "mismatch"
  },
  "components": {
    "litellm": { "status": "ok", "latency_ms": 25, "message": "ok" },
    "vllm": { "status": "ok", "latency_ms": 40, "message": "ok" }
  },
  "warnings": [
    "LiteLLM VLLM_MODEL_ID does not match the model reported by vLLM. Run scripts/sync-active-model.ps1."
  ]
}
```

Status codes:

```text
200 status returned even if degraded
500 status endpoint crashed unexpectedly
```

### 10.2 Platform status page

Name: Platform Status Page

Method:

```text
GET
```

Path:

```text
/status
```

Behavior:

1. Render readable HTML.
2. Do not require JavaScript.
3. Do not expose secrets.
4. Show PASS/WARN/FAIL states.
5. Link to OpenWebUI, Grafana, Prometheus, and benchmark dashboard pages.

### 10.3 Model sync status CLI contract

Script:

```text
scripts/sync-active-model.ps1
```

Success output should include:

```text
Detected vLLM model: qwen36-35b-a3b
Current LiteLLM VLLM_MODEL_ID: openai/qwen36-27b
Updated LiteLLM VLLM_MODEL_ID: openai/qwen36-35b-a3b
Recreated LiteLLM service: ok
LiteLLM health: ok
```

Failure output should include:

```text
FAIL Could not read http://127.0.0.1:8000/v1/models
Next step: check the Lanta job and SSH tunnel.
```

## 11. Files likely involved

Create:

```text
scripts/sync-active-model.ps1

lanta/scripts/lanta-metrics-exporter.py
# or
observability/exporters/lanta_gpu_exporter.py

dashboard/backend/app/routers/platform_status.py
```

Modify:

```text
README.md
docs/ARCHITECTURE.md
docs/OPERATIONS.md
docs/BENCHMARKING.md
HOW_TO_SWAP.md
scripts/check-platform.ps1
litellm/README.md
litellm/.env.example
litellm/config.yaml
observability/README.md
observability/.env.example
observability/docker-compose.yml
observability/prometheus/prometheus.yml
observability/grafana/dashboards/lanta-llm-operations.json
benchmark/runners/run_suite.py
benchmark/storage/models.py
benchmark/storage/db.py
benchmark/schemas/result.schema.json
dashboard/backend/app/main.py
dashboard/backend/app/schemas.py
dashboard/backend/app/routers/pages.py
tests/test_benchmark_core.py
tests/test_dashboard_helpers.py
tests/test_platform_exporter.py
```

Add benchmark cases:

```text
benchmark/cases/rfid_basic/
  edge_detector.yaml
  clock_enable_counter.yaml
  spi_register_bank.yaml
  uart_rx_debug.yaml
  rfid_crc16.yaml
  testbench_edge_detector.yaml
  low_power_rewrite_counter.yaml

benchmark/fixtures/
  edge_detector.sv
  broken_uart_rx.sv
  crc16_reference.sv
```

Do not delete:

```text
website/
sharing/
lanta/scripts/
windows/tunnel/
```

## 12. Edge cases

1. vLLM tunnel is down during model sync.
2. vLLM `/models` returns empty data.
3. vLLM `/models` returns multiple models.
4. `litellm/.env` is missing.
5. `litellm/.env` exists but has no `VLLM_MODEL_ID`.
6. `.env` has duplicate `VLLM_MODEL_ID` lines.
7. Docker is not running.
8. Docker Compose command fails.
9. LiteLLM takes time to restart and initially returns empty reply.
10. OpenWebUI still shows old model list due to persistent settings.
11. User changed `LITELLM_MASTER_KEY` but did not update OpenWebUI API key.
12. Postgres volume keeps old password after `.env` change.
13. Prometheus starts before exporters.
14. Grafana starts before Prometheus.
15. Lanta exporter is not enabled.
16. `nvidia-smi` is not available.
17. Lanta exporter runs on login node instead of GPU node.
18. Slurm job is pending, not running.
19. Slurm job is running but vLLM not ready yet.
20. Model swap happens during benchmark run.
21. Benchmark run records alias but model changes before completion.
22. LiteLLM token metrics are missing or renamed by LiteLLM version change.
23. API key/user label in metrics is missing.
24. Dashboard cannot reach Grafana because of container networking.
25. Health check should not expose secrets in error messages.

## 13. Testing plan

### 13.1 Unit tests

Add tests for:

1. Parsing vLLM `/models` response.
2. Normalizing model id to `openai/<model>`.
3. Updating `VLLM_MODEL_ID` in `.env` content.
4. Preserving unrelated `.env` lines.
5. Detecting model mismatch.
6. Platform status aggregation.
7. Dashboard status schema.
8. Benchmark metadata includes resolved model.
9. Lanta exporter metric formatting.
10. GPU exporter behavior when `nvidia-smi` is missing.
11. Slurm parser for `squeue` output.
12. Artifact path safety still rejects traversal.
13. Benchmark failure category naming.

Example test names:

```text
test_normalize_model_adds_openai_prefix
test_normalize_model_keeps_existing_provider_prefix
test_update_env_replaces_vllm_model_id
test_update_env_adds_vllm_model_id_when_missing
test_platform_status_reports_model_mismatch
test_benchmark_records_resolved_model_metadata
test_lanta_exporter_reports_gpu_unavailable_without_nvidia_smi
```

### 13.2 Integration tests

Add integration tests for:

1. `GET /api/platform/status` returns valid shape.
2. `/status` page renders without benchmark data.
3. `check-platform.ps1` can run with mocked endpoints if practical.
4. Benchmark runner records model metadata when vLLM endpoint is mocked.
5. Prometheus config validates.
6. Grafana dashboard JSON is valid JSON.
7. Docker Compose config validates for all Compose files.

### 13.3 Manual tests

Manual model sync test:

```powershell
cd D:\ArmmyWorkspace\SiliconCraft\lanta-llm-hosting
powershell -ExecutionPolicy Bypass -File .\scripts\sync-active-model.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\check-platform.ps1
```

Manual LiteLLM check:

```powershell
$env:LITELLM_MASTER_KEY="sk-your-key"
curl.exe http://127.0.0.1:4000/v1/models -H "Authorization: Bearer $env:LITELLM_MASTER_KEY"
```

Manual chat check:

```powershell
curl.exe http://127.0.0.1:4000/v1/chat/completions `
  -H "Authorization: Bearer $env:LITELLM_MASTER_KEY" `
  -H "Content-Type: application/json" `
  -d "{\"model\":\"active-lanta-model\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply exactly: online\"}],\"temperature\":0,\"max_tokens\":8}"
```

Manual dashboard check:

```powershell
curl.exe http://127.0.0.1:8088/api/healthz
curl.exe http://127.0.0.1:8088/api/platform/status
```

Manual observability check:

```powershell
curl.exe http://127.0.0.1:9108/metrics
curl.exe http://127.0.0.1:9090/-/ready
curl.exe http://127.0.0.1:3002/api/health
```

### 13.4 Validation commands

Run:

```bash
python -m compileall benchmark dashboard observability
python -m pytest
docker compose -f litellm/docker-compose.yml config
docker compose -f openwebui/docker-compose.yml config
docker compose -f observability/docker-compose.yml config
docker compose -f dashboard/docker-compose.yml config
```

If PowerShell scripts are changed, manually run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-platform.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\sync-active-model.ps1 -NoRestart
```

## 14. Definition of done

Phase 2 is complete only when:

1. `scripts/sync-active-model.ps1` exists and can update `VLLM_MODEL_ID` from vLLM `/models`.
2. `scripts/check-platform.ps1` reports model identity and mismatch warnings.
3. LiteLLM still exposes `active-lanta-model`.
4. The real upstream model is visible in a status page/API or Grafana panel.
5. Dashboard exposes `GET /api/platform/status`.
6. Dashboard has a readable `/status` page.
7. Benchmark runs record alias and resolved upstream model.
8. At least one expanded `rfid_basic` benchmark suite exists.
9. Grafana clearly labels LiteLLM token metrics vs real GPU metrics.
10. GPU panels either show real Lanta metrics or clear setup instructions.
11. Optional Lanta exporter is documented and safe by default.
12. Docs explain stable alias vs real model.
13. Docs explain model swap and sync workflow.
14. Tests are added or updated.
15. Existing OpenWebUI, LiteLLM, observability, dashboard, benchmark, website, sharing, Lanta scripts, and tunnel flows remain usable.
16. No real secrets or `.env` files are committed.

## 15. Codex implementation instructions

Implement Phase 2 in small, safe steps.

Priority order:

1. Add `scripts/sync-active-model.ps1`.
2. Improve `scripts/check-platform.ps1` with model identity checks.
3. Add dashboard `/api/platform/status` and `/status` page.
4. Update docs for model swap, sync, and status visibility.
5. Add benchmark model metadata recording.
6. Add `rfid_basic` benchmark suite.
7. Improve Grafana labels and no-data guidance.
8. Add optional Lanta GPU exporter.

Do not introduce unnecessary complexity.

Do not break the current working stack.

Do not delete existing folders.

Do not commit secrets.

Prefer simple PowerShell and Python scripts that are easy for a Windows-based intern to run.

At the end of implementation, summarize:

1. Files created.
2. Files modified.
3. How to sync after a Lanta model swap.
4. How to check platform health.
5. Where to see the real active model.
6. Whether GPU metrics are real or still optional.
7. How to run the expanded benchmark suite.
8. Tests run and tests not run.
