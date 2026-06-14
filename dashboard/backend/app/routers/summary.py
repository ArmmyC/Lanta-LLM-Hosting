from __future__ import annotations

from statistics import mean

from fastapi import APIRouter, HTTPException

from ..database import load_store
from ..schemas import parse_iso_datetime

router = APIRouter(prefix="/api/benchmark")


def rate(results: list[dict[str, object]], key: str, success: str = "passed") -> float:
    values = [item for item in results if item.get(key) is not None]
    if not values:
        return 0.0
    return len([item for item in values if item.get(key) == success]) / len(values)


@router.get("/summary")
def summary(
    since: str | None = None,
    model_alias: str | None = None,
    prompt_version: str | None = None,
    suite_name: str | None = None,
) -> dict[str, object]:
    if since:
        try:
            since_dt = parse_iso_datetime(since)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="since must be an ISO datetime") from exc
    else:
        since_dt = None

    data = load_store()
    runs = [
        run
        for run in data["runs"]
        if (not model_alias or run.get("model_alias") == model_alias)
        and (not prompt_version or run.get("prompt_version") == prompt_version)
        and (not suite_name or run.get("suite_name") == suite_name)
        and (not since_dt or parse_iso_datetime(str(run.get("started_at"))) >= since_dt)
    ]
    run_ids = {run["id"] for run in runs}
    results = [item for item in data["results"] if item.get("run_id") in run_ids]
    latencies = [int(item["latency_ms"]) for item in results if item.get("latency_ms") is not None]
    tokens = [int(item["total_tokens"]) for item in results if item.get("total_tokens") is not None]
    by_model = []
    for model in sorted({str(item.get("model_alias")) for item in results}):
        model_results = [item for item in results if item.get("model_alias") == model]
        by_model.append(
            {
                "model_alias": model,
                "total_results": len(model_results),
                "pass_rate": rate(model_results, "status"),
                "compile_pass_rate": rate(model_results, "compile_status"),
                "simulation_pass_rate": rate(model_results, "simulation_status"),
            }
        )
    failure_categories = []
    for category in sorted({str(item.get("failure_category")) for item in results if item.get("failure_category") not in {None, "none"}}):
        failure_categories.append({"failure_category": category, "count": len([item for item in results if item.get("failure_category") == category])})
    return {
        "total_runs": len(runs),
        "total_results": len(results),
        "pass_rate": rate(results, "status"),
        "compile_pass_rate": rate(results, "compile_status"),
        "simulation_pass_rate": rate(results, "simulation_status"),
        "average_latency_ms": mean(latencies) if latencies else 0,
        "average_total_tokens": mean(tokens) if tokens else 0,
        "by_model": by_model,
        "failure_categories": failure_categories,
    }
