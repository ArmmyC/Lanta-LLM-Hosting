from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
router = APIRouter()


@router.get("/api/healthz")
def healthz() -> dict[str, object]:
    return {
        "ok": True,
        "service": "lanta-status-dashboard",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
