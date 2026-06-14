from __future__ import annotations

from observability.exporters.platform_exporter import metric


def test_metric_escapes_labels() -> None:
    rendered = metric("demo_metric", 1, {"message": "a \"quoted\" value"})
    assert rendered == 'demo_metric{message="a \\"quoted\\" value"} 1'
