from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..database import load_store, safe_artifact_path
from ..schemas import RUN_STATUSES, validate_run_id

router = APIRouter(prefix="/api/benchmark")


@router.get("/runs")
def list_runs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    model_alias: str | None = None,
    prompt_version: str | None = None,
    status: str | None = None,
    suite_name: str | None = None,
) -> dict[str, object]:
    if status and status not in RUN_STATUSES:
        raise HTTPException(status_code=400, detail="unsupported status")
    runs = load_store()["runs"]
    filtered = [
        run
        for run in runs
        if (not model_alias or run.get("model_alias") == model_alias)
        and (not prompt_version or run.get("prompt_version") == prompt_version)
        and (not status or run.get("status") == status)
        and (not suite_name or run.get("suite_name") == suite_name)
    ]
    return {"items": filtered[offset : offset + limit], "limit": limit, "offset": offset, "total": len(filtered)}


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, object]:
    if not validate_run_id(run_id):
        raise HTTPException(status_code=404, detail="benchmark run not found")
    data = load_store()
    run = next((item for item in data["runs"] if item.get("id") == run_id), None)
    if not run:
        raise HTTPException(status_code=404, detail="benchmark run not found")
    results = [item for item in data["results"] if item.get("run_id") == run_id]
    return {**run, "results": results}


@router.get("/artifacts/{result_id}/{artifact_type}")
def get_artifact(result_id: str, artifact_type: str) -> dict[str, object]:
    allowed = {
        "raw_response": "raw_response_path",
        "extracted_code": "extracted_code_path",
        "compile_log": "compile_log_path",
        "simulation_log": "simulation_log_path",
    }
    if artifact_type not in allowed:
        raise HTTPException(status_code=404, detail="artifact not found")
    result = next((item for item in load_store()["results"] if item.get("id") == result_id), None)
    if not result:
        raise HTTPException(status_code=404, detail="artifact not found")
    path = safe_artifact_path(result.get(allowed[artifact_type]) or "")
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="artifact not found")
    return {
        "result_id": result_id,
        "artifact_type": artifact_type,
        "content_type": "text/plain",
        "content": path.read_text(encoding="utf-8"),
    }

