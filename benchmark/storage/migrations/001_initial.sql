CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS benchmark_suites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS benchmark_cases (
  id TEXT PRIMARY KEY,
  suite_id UUID NULL REFERENCES benchmark_suites(id),
  title TEXT NOT NULL,
  task_type TEXT NOT NULL,
  description TEXT NULL,
  prompt TEXT NOT NULL,
  expected_language TEXT NOT NULL DEFAULT 'systemverilog',
  expected_module_name TEXT NULL,
  timeout_seconds INTEGER NOT NULL DEFAULT 120,
  evaluator_config JSONB NOT NULL DEFAULT '{}',
  case_file_path TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_benchmark_cases_task_type ON benchmark_cases(task_type);
CREATE INDEX IF NOT EXISTS idx_benchmark_cases_suite_id ON benchmark_cases(suite_id);
CREATE INDEX IF NOT EXISTS idx_benchmark_cases_expected_module_name ON benchmark_cases(expected_module_name);

CREATE TABLE IF NOT EXISTS prompt_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT NULL,
  content TEXT NOT NULL,
  content_sha256 TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS benchmark_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  suite_name TEXT NOT NULL,
  model_alias TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ NULL,
  duration_ms INTEGER NULL,
  total_cases INTEGER NOT NULL DEFAULT 0,
  passed_cases INTEGER NOT NULL DEFAULT 0,
  failed_cases INTEGER NOT NULL DEFAULT 0,
  error_cases INTEGER NOT NULL DEFAULT 0,
  config JSONB NOT NULL DEFAULT '{}',
  created_by TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_benchmark_runs_started_at ON benchmark_runs(started_at);
CREATE INDEX IF NOT EXISTS idx_benchmark_runs_model_alias ON benchmark_runs(model_alias);
CREATE INDEX IF NOT EXISTS idx_benchmark_runs_prompt_version ON benchmark_runs(prompt_version);
CREATE INDEX IF NOT EXISTS idx_benchmark_runs_status ON benchmark_runs(status);

CREATE TABLE IF NOT EXISTS benchmark_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES benchmark_runs(id) ON DELETE CASCADE,
  case_id TEXT NOT NULL REFERENCES benchmark_cases(id),
  model_alias TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  status TEXT NOT NULL,
  failure_category TEXT NULL,
  failure_message TEXT NULL,
  request_started_at TIMESTAMPTZ NULL,
  request_finished_at TIMESTAMPTZ NULL,
  latency_ms INTEGER NULL,
  input_tokens INTEGER NULL,
  output_tokens INTEGER NULL,
  total_tokens INTEGER NULL,
  raw_response_path TEXT NULL,
  extracted_code_path TEXT NULL,
  compile_status TEXT NULL,
  compile_log_path TEXT NULL,
  simulation_status TEXT NULL,
  simulation_log_path TEXT NULL,
  score NUMERIC NULL,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_benchmark_results_run_id ON benchmark_results(run_id);
CREATE INDEX IF NOT EXISTS idx_benchmark_results_case_id ON benchmark_results(case_id);
CREATE INDEX IF NOT EXISTS idx_benchmark_results_model_alias ON benchmark_results(model_alias);
CREATE INDEX IF NOT EXISTS idx_benchmark_results_prompt_version ON benchmark_results(prompt_version);
CREATE INDEX IF NOT EXISTS idx_benchmark_results_status ON benchmark_results(status);
CREATE INDEX IF NOT EXISTS idx_benchmark_results_failure_category ON benchmark_results(failure_category);

CREATE TABLE IF NOT EXISTS platform_health_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  checked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  component TEXT NOT NULL,
  status TEXT NOT NULL,
  latency_ms INTEGER NULL,
  message TEXT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_platform_health_checks_checked_at ON platform_health_checks(checked_at);
CREATE INDEX IF NOT EXISTS idx_platform_health_checks_component ON platform_health_checks(component);
CREATE INDEX IF NOT EXISTS idx_platform_health_checks_status ON platform_health_checks(status);
