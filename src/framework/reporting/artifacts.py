from __future__ import annotations

from pathlib import Path


def ensure_artifact_dir(path: str) -> Path:
    artifact_dir = Path(path)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir

