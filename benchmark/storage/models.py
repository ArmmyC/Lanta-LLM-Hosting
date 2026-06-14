from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class BenchmarkRun:
    id: str = field(default_factory=lambda: str(uuid4()))
    suite_name: str = "smoke"
    model_alias: str = "active-lanta-model"
    prompt_version: str = "rfid_low_power_v1"
    status: str = "running"
    started_at: str = field(default_factory=utc_now)
    finished_at: str | None = None
    duration_ms: int | None = None
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    error_cases: int = 0
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    id: str = field(default_factory=lambda: str(uuid4()))
    run_id: str = ""
    case_id: str = ""
    model_alias: str = "active-lanta-model"
    prompt_version: str = "rfid_low_power_v1"
    status: str = "skipped"
    failure_category: str | None = None
    failure_message: str | None = None
    request_started_at: str | None = None
    request_finished_at: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    raw_response_path: str | None = None
    extracted_code_path: str | None = None
    compile_status: str | None = "not_run"
    compile_log_path: str | None = None
    simulation_status: str | None = "not_run"
    simulation_log_path: str | None = None
    score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

