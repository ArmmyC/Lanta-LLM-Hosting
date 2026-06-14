from __future__ import annotations

import re


def classify_static_failure(code: str, expected_module_name: str | None, required_terms: list[str] | None = None) -> tuple[str, str | None]:
    if not code.strip():
        return "failed", "no_code_block"
    if expected_module_name:
        pattern = rf"\bmodule\s+{re.escape(expected_module_name)}\b"
        if not re.search(pattern, code):
            return "failed", "wrong_module_name"
    for term in required_terms or []:
        if term not in code:
            return "failed", "missing_port"
    return "passed", "none"


def numeric_score(status: str) -> float:
    return 1.0 if status == "passed" else 0.0

