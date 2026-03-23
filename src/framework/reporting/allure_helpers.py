from __future__ import annotations

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
    allure.attach(str(content), name=name, attachment_type=allure.attachment_type.JSON)


def attach_file(path: str | Path, name: str) -> None:
    if allure is None:
        return
    allure.attach.file(str(path), name=name)
