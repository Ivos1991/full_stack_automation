from __future__ import annotations

import pytest

from src.framework.config.settings import Settings, get_settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()

