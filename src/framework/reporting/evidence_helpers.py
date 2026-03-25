from __future__ import annotations
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any
from src.framework.reporting.allure_helpers import attach_file, attach_json

def serialize_report_value(value: Any) -> Any:
    """Convert framework objects into stable JSON-safe structures for Allure evidence."""
    if is_dataclass(value):
        return {key: serialize_report_value(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): serialize_report_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serialize_report_value(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "__dict__") and not isinstance(value, type):
        return {key: serialize_report_value(item) for key, item in vars(value).items()}
    return value


def attach_snapshot(name: str, content: Any | None = None, **sections: Any) -> None:
    """Attach structured test evidence without forcing raw attachment formatting into the test body."""
    if content is not None and sections:
        raise ValueError("attach_snapshot accepts either content or named sections, not both.")

    payload = content if content is not None else sections
    attach_json(name=name, content=serialize_report_value(payload))


def attach_ui_snapshot(
    *,
    name: str,
    screenshot_path: str | Path | None = None,
    content: Any | None = None,
    **sections: Any,
) -> None:
    """Attach a UI screenshot and matching structured evidence through one test-layer helper."""
    if screenshot_path is not None:
        attach_file(path=screenshot_path, name=name)
    attach_snapshot(name=f"{name}-state", content=content, **sections)
