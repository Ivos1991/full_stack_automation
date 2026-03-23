from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os
from urllib.parse import urlparse

import requests


def _get_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return int(raw_value)


def _read_key_from_env_file(path: Path, key: str) -> str | None:
    if not path.exists():
        return None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        current_key, value = line.split("=", 1)
        if current_key.strip() == key:
            return value.strip().strip('"').strip("'")

    return None


def _resolve_rwa_root_path() -> Path | None:
    raw_path = os.getenv("RWA_ROOT_PATH")
    if not raw_path:
        return None

    expanded_path = Path(raw_path).expanduser()
    return expanded_path.resolve(strict=False)


def _extract_runtime_backend_port(runtime_config_path: Path) -> int | None:
    if not runtime_config_path.exists():
        return None

    content = runtime_config_path.read_text(encoding="utf-8")
    marker = "__RWA_BACKEND_PORT__ = "
    if marker not in content:
        return None

    raw_port = content.split(marker, 1)[1].split(";", 1)[0].strip()
    return int(raw_port) if raw_port.isdigit() else None


def _can_reach_rwa_api(base_url: str) -> bool:
    try:
        response = requests.post(
            f"{base_url.rstrip('/')}/login",
            json={"username": "health-check", "password": "health-check"},
            timeout=2,
        )
    except requests.RequestException:
        return False

    return response.status_code not in {404, 405, 500, 502, 503, 504}


def _resolve_base_url() -> str:
    explicit_base_url = os.getenv("BASE_URL")
    if explicit_base_url:
        return explicit_base_url.rstrip("/")

    rwa_root = _resolve_rwa_root_path()
    rwa_env_path = rwa_root / ".env" if rwa_root else None
    frontend_port = _read_key_from_env_file(rwa_env_path, "PORT") if rwa_env_path else None
    frontend_port = frontend_port or "3000"
    return f"http://localhost:{frontend_port}"


def _resolve_api_base_url(base_url: str) -> str:
    explicit_api_base_url = os.getenv("API_BASE_URL")
    if explicit_api_base_url:
        return explicit_api_base_url.rstrip("/")

    rwa_root = _resolve_rwa_root_path()
    rwa_env_path = rwa_root / ".env" if rwa_root else None
    runtime_config_path = rwa_root / "public" / "runtime-config.js" if rwa_root else None

    configured_port = _read_key_from_env_file(rwa_env_path, "VITE_BACKEND_PORT") if rwa_env_path else None
    configured_port = configured_port or "3001"
    runtime_port = _extract_runtime_backend_port(runtime_config_path) if runtime_config_path else None
    frontend_port = urlparse(base_url).port or 3000

    candidate_ports: list[int] = []
    for raw_port in (runtime_port, int(configured_port), frontend_port + 1, 3001, 3002, 3003):
        if raw_port not in candidate_ports:
            candidate_ports.append(raw_port)

    for port in candidate_ports:
        candidate_url = f"http://localhost:{port}"
        if _can_reach_rwa_api(candidate_url):
            return candidate_url

    return f"http://localhost:{configured_port}"


@dataclass(frozen=True)
class Settings:
    rwa_root_path: str | None
    base_url: str
    api_base_url: str
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = _get_int("DB_PORT", 5432)
    db_name: str = os.getenv("DB_NAME", "realworld")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    rwa_data_file: str = os.getenv("RWA_DATA_FILE", "")
    headless: bool = _get_bool("HEADLESS", True)
    default_timeout_ms: int = _get_int("DEFAULT_TIMEOUT_MS", 10000)
    allure_results_dir: str = os.getenv("ALLURE_RESULTS_DIR", "artifacts/allure-results")
    screenshots_dir: str = os.getenv("SCREENSHOTS_DIR", "artifacts/screenshots")
    traces_dir: str = os.getenv("TRACES_DIR", "artifacts/traces")
    videos_dir: str = os.getenv("VIDEOS_DIR", "artifacts/videos")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    rwa_root = _resolve_rwa_root_path()
    base_url = _resolve_base_url()
    api_base_url = _resolve_api_base_url(base_url)
    rwa_data_file = os.getenv("RWA_DATA_FILE")
    if not rwa_data_file and rwa_root:
        rwa_data_file = str(rwa_root / "data" / "database.json")

    return Settings(
        rwa_root_path=str(rwa_root) if rwa_root else None,
        base_url=base_url,
        api_base_url=api_base_url,
        rwa_data_file=rwa_data_file or "",
    )
