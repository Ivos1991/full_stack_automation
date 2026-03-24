from __future__ import annotations
import pytest
from pathlib import Path
from src.framework.config.settings import get_settings

try:
    import allure
except ImportError:  # pragma: no cover - fallback for environments without allure
    allure = None


@pytest.fixture(scope="session", autouse=True)
def allure_environment() -> None:
    settings = get_settings()
    results_dir = Path(settings.allure_results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    environment_file = results_dir / "environment.properties"
    environment_file.write_text(
        "\n".join(
            [
                f"BASE_URL={settings.base_url}",
                f"API_BASE_URL={settings.api_base_url}",
                f"DB_HOST={settings.db_host}",
            ]
        ),
        encoding="utf-8",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def attach_test_name(request: pytest.FixtureRequest) -> None:
    if allure is not None:
        allure.dynamic.title(request.node.name)
