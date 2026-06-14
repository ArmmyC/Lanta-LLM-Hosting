from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def compile_systemverilog(source_path: Path, timeout_seconds: int) -> tuple[str, str]:
    tool = shutil.which("iverilog")
    if not tool:
        return "tool_missing", "iverilog not found; compile evaluator skipped."
    output_path = source_path.with_suffix(".vvp")
    try:
        result = subprocess.run(
            [tool, "-g2012", "-o", str(output_path), str(source_path)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "timeout", f"compile timed out after {timeout_seconds}s"
    log = (result.stdout or "") + (result.stderr or "")
    return ("passed" if result.returncode == 0 else "failed"), log

