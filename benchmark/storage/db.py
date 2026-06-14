from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any


class JsonResultStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"runs": [], "results": [], "cases": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def record_case(self, case: dict[str, Any]) -> None:
        data = self.load()
        existing = {item["id"]: item for item in data["cases"]}
        existing[case["id"]] = case
        data["cases"] = list(existing.values())
        self.save(data)

    def record_run(self, run: Any) -> None:
        data = self.load()
        run_dict = asdict(run) if hasattr(run, "__dataclass_fields__") else dict(run)
        data["runs"] = [item for item in data["runs"] if item["id"] != run_dict["id"]]
        data["runs"].append(run_dict)
        self.save(data)

    def record_result(self, result: Any) -> None:
        data = self.load()
        result_dict = asdict(result) if hasattr(result, "__dataclass_fields__") else dict(result)
        data["results"] = [item for item in data["results"] if item["id"] != result_dict["id"]]
        data["results"].append(result_dict)
        self.save(data)


def default_json_store(root: Path) -> JsonResultStore:
    return JsonResultStore(root / "benchmark" / "results" / "benchmark-results.json")


def database_url() -> str | None:
    return os.environ.get("BENCHMARK_DATABASE_URL") or os.environ.get("DATABASE_URL")


class PostgresResultStore:
    def __init__(self, url: str) -> None:
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - depends on optional deployment extra
            raise RuntimeError("psycopg is required for PostgreSQL benchmark storage") from exc
        self.psycopg = psycopg
        self.url = url

    def _execute(self, query: str, params: tuple[Any, ...]) -> None:
        with self.psycopg.connect(self.url) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)

    def record_case(self, case: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO benchmark_cases (
              id, title, task_type, description, prompt, expected_language,
              expected_module_name, timeout_seconds, evaluator_config, case_file_path
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (id) DO UPDATE SET
              title = EXCLUDED.title,
              task_type = EXCLUDED.task_type,
              description = EXCLUDED.description,
              prompt = EXCLUDED.prompt,
              expected_language = EXCLUDED.expected_language,
              expected_module_name = EXCLUDED.expected_module_name,
              timeout_seconds = EXCLUDED.timeout_seconds,
              evaluator_config = EXCLUDED.evaluator_config,
              case_file_path = EXCLUDED.case_file_path,
              updated_at = now()
            """,
            (
                case["id"],
                case["title"],
                case["task_type"],
                case.get("description"),
                case["prompt"],
                case.get("expected_language", "systemverilog"),
                case.get("expected_module_name"),
                case.get("timeout_seconds", 120),
                json.dumps(case.get("evaluator_config", {})),
                case.get("case_file_path"),
            ),
        )

    def record_run(self, run: Any) -> None:
        item = asdict(run) if hasattr(run, "__dataclass_fields__") else dict(run)
        self._execute(
            """
            INSERT INTO benchmark_runs (
              id, suite_name, model_alias, prompt_version, status, started_at, finished_at,
              duration_ms, total_cases, passed_cases, failed_cases, error_cases, config
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (id) DO UPDATE SET
              status = EXCLUDED.status,
              finished_at = EXCLUDED.finished_at,
              duration_ms = EXCLUDED.duration_ms,
              total_cases = EXCLUDED.total_cases,
              passed_cases = EXCLUDED.passed_cases,
              failed_cases = EXCLUDED.failed_cases,
              error_cases = EXCLUDED.error_cases,
              config = EXCLUDED.config
            """,
            (
                item["id"],
                item["suite_name"],
                item["model_alias"],
                item["prompt_version"],
                item["status"],
                item["started_at"],
                item["finished_at"],
                item["duration_ms"],
                item["total_cases"],
                item["passed_cases"],
                item["failed_cases"],
                item["error_cases"],
                json.dumps(item["config"]),
            ),
        )

    def record_result(self, result: Any) -> None:
        item = asdict(result) if hasattr(result, "__dataclass_fields__") else dict(result)
        self._execute(
            """
            INSERT INTO benchmark_results (
              id, run_id, case_id, model_alias, prompt_version, status, failure_category,
              failure_message, request_started_at, request_finished_at, latency_ms,
              input_tokens, output_tokens, total_tokens, raw_response_path,
              extracted_code_path, compile_status, compile_log_path, simulation_status,
              simulation_log_path, score, metadata, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                item["id"],
                item["run_id"],
                item["case_id"],
                item["model_alias"],
                item["prompt_version"],
                item["status"],
                item["failure_category"],
                item["failure_message"],
                item["request_started_at"],
                item["request_finished_at"],
                item["latency_ms"],
                item["input_tokens"],
                item["output_tokens"],
                item["total_tokens"],
                item["raw_response_path"],
                item["extracted_code_path"],
                item["compile_status"],
                item["compile_log_path"],
                item["simulation_status"],
                item["simulation_log_path"],
                item["score"],
                json.dumps(item["metadata"]),
                item["created_at"],
            ),
        )


def result_store(root: Path) -> JsonResultStore | PostgresResultStore:
    url = database_url()
    if url:
        return PostgresResultStore(url)
    return default_json_store(root)
