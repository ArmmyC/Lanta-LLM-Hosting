from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmark.evaluators.extract_code import extract_code_block
from benchmark.runners.run_suite import build_chat_payload, load_case, parse_usage, validate_case
from benchmark.evaluators.score import classify_static_failure


def test_extract_code_returns_first_systemverilog_block() -> None:
    response = """```python
print("no")
```
```systemverilog
module lp_counter; endmodule
```"""
    extraction = extract_code_block(response)
    assert extraction.language == "systemverilog"
    assert "module lp_counter" in extraction.code


def test_extract_code_returns_largest_block_without_language() -> None:
    response = """```
short
```
```
module bigger; endmodule
```"""
    extraction = extract_code_block(response)
    assert "module bigger" in extraction.code


def test_extract_code_classifies_empty_response() -> None:
    extraction = extract_code_block("no code here")
    assert extraction.failure_category == "no_code_block"


def test_case_validator_rejects_invalid_task_type() -> None:
    with pytest.raises(ValueError):
        validate_case({"id": "bad_case", "title": "Bad", "task_type": "bad", "prompt": "x", "timeout_seconds": 10})


def test_case_validator_requires_rtl_module_name() -> None:
    with pytest.raises(ValueError):
        validate_case({"id": "rtl_bad", "title": "Bad", "task_type": "rtl_generation", "prompt": "x", "timeout_seconds": 10})


def test_static_failure_wrong_module_name() -> None:
    status, failure = classify_static_failure("module other; endmodule", "lp_counter")
    assert status == "failed"
    assert failure == "wrong_module_name"


def test_load_smoke_case() -> None:
    case = load_case(Path("benchmark/cases/smoke/rtl_counter.yaml"))
    assert case["id"] == "rtl_counter"
    assert case["expected_language"] == "systemverilog"


def test_litellm_payload_construction() -> None:
    messages = [{"role": "user", "content": "hi"}]
    payload = build_chat_payload(messages, "active-lanta-model")
    assert payload["model"] == "active-lanta-model"
    assert payload["messages"] == messages
    assert payload["temperature"] == 0


def test_token_usage_parsing() -> None:
    usage = parse_usage({"usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3}})
    assert usage == {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3}
