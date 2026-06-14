from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..database import load_store

router = APIRouter()


@router.get("/api/healthz")
def healthz() -> dict[str, object]:
    try:
        load_store()
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"ok": False, "service": "benchmark-dashboard", "database": "down", "error": str(exc)},
        )
    return {
        "ok": True,
        "service": "benchmark-dashboard",
        "database": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
