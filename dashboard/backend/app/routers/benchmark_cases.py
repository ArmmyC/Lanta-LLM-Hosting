from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..database import load_store
from ..schemas import TASK_TYPES, validate_case_id

router = APIRouter(prefix="/api/benchmark")


@router.get("/cases")
def list_cases(
    suite_name: str | None = None,
    task_type: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, object]:
    if task_type and task_type not in TASK_TYPES:
        raise HTTPException(status_code=400, detail="unsupported task_type")
    cases = load_store()["cases"]
    filtered = [
        case
        for case in cases
        if (not task_type or case.get("task_type") == task_type)
        and (not suite_name or suite_name in str(case.get("case_file_path", "")))
    ]
    return {"items": filtered[offset : offset + limit], "limit": limit, "offset": offset, "total": len(filtered)}


@router.get("/cases/{case_id}")
def get_case(case_id: str) -> dict[str, object]:
    if not validate_case_id(case_id):
        raise HTTPException(status_code=404, detail="benchmark case not found")
    data = load_store()
    case = next((item for item in data["cases"] if item.get("id") == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="benchmark case not found")
    latest_results = [item for item in data["results"] if item.get("case_id") == case_id][-10:]
    return {**case, "latest_results": latest_results}

