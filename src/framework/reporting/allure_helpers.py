from __future__ import annotations
import json
from pathlib import Path
from typing import Any

try:
    import allure
except ImportError:  # pragma: no cover - optional locally
    allure = None


def attach_text(name: str, content: str) -> None:
    if allure is None:
        return
    allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_json(name: str, content: Any) -> None:
    if allure is None:
        return
    allure.attach(
        json.dumps(content, indent=2, sort_keys=True, ensure_ascii=True, default=str),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_file(path: str | Path, name: str) -> None:
    if allure is None:
        return
    allure.attach.file(str(path), name=name)
