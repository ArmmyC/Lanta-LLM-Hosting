from __future__ import annotations

import re
from dataclasses import dataclass


CODE_BLOCK_RE = re.compile(r"```(?P<lang>[a-zA-Z0-9_+-]*)\s*\n(?P<code>.*?)```", re.DOTALL)
SV_LANGS = {"systemverilog", "sv", "verilog", "v"}


@dataclass(frozen=True)
class CodeExtraction:
    code: str
    language: str | None
    failure_category: str | None = None


def extract_code_block(response_text: str) -> CodeExtraction:
    blocks = [
        (match.group("lang").strip().lower() or None, match.group("code").strip())
        for match in CODE_BLOCK_RE.finditer(response_text or "")
    ]
    if not blocks:
        return CodeExtraction(code="", language=None, failure_category="no_code_block")

    for language, code in blocks:
        if language in SV_LANGS:
            return CodeExtraction(code=code, language=language)

    language, code = max(blocks, key=lambda item: len(item[1]))
    return CodeExtraction(code=code, language=language)

