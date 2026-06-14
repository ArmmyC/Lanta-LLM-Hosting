from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def simulate_vvp(compiled_path: Path, timeout_seconds: int) -> tuple[str, str]:
    tool = shutil.which("vvp")
    if not tool:
        return "tool_missing", "vvp not found; simulation evaluator skipped."
    if not compiled_path.exists():
        return "not_run", "compiled artifact missing; simulation not run."
    try:
        result = subprocess.run(
            [tool, str(compiled_path)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "timeout", f"simulation timed out after {timeout_seconds}s"
    log = (result.stdout or "") + (result.stderr or "")
    return ("passed" if result.returncode == 0 else "failed"), log
