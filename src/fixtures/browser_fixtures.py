from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from src.framework.config.settings import Settings
from src.framework.reporting.artifacts import ensure_artifact_dir

if TYPE_CHECKING:
    from playwright.sync_api import Browser, BrowserContext, Page, Playwright


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Any, None, None]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:  # pragma: no cover - depends on local environment
        pytest.skip(f"Playwright is not installed in the current environment: {error}")

    try:
        with sync_playwright() as playwright:
            yield playwright
    except PermissionError as error:  # pragma: no cover - depends on local Windows process permissions
        pytest.skip(f"Playwright could not start in the current environment: {error}")


@pytest.fixture(scope="session")
def browser(playwright_instance: Any, settings: Settings) -> Generator[Any, None, None]:
    try:
        browser = playwright_instance.chromium.launch(headless=settings.headless)
    except PermissionError as error:  # pragma: no cover - depends on local Windows process permissions
        pytest.skip(f"Chromium could not launch in the current environment: {error}")
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Any, settings: Settings, request: pytest.FixtureRequest) -> Generator[Any, None, None]:
    video_dir = ensure_artifact_dir(settings.videos_dir)

    browser_context = browser.new_context(record_video_dir=str(video_dir))
    browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield browser_context

    trace_dir = ensure_artifact_dir(settings.traces_dir)
    trace_path = trace_dir / f"{request.node.name}.zip"
    browser_context.tracing.stop(path=str(trace_path))
    browser_context.close()


@pytest.fixture(scope="function")
def page(context: Any, settings: Settings, request: pytest.FixtureRequest) -> Generator[Any, None, None]:
    try:
        import allure
    except ImportError:  # pragma: no cover - optional locally
        allure = None

    browser_page = context.new_page()
    browser_page.set_default_timeout(settings.default_timeout_ms)
    yield browser_page

    failed = getattr(request.node, "rep_call", None)
    if failed and failed.failed:
        screenshot_dir = ensure_artifact_dir(settings.screenshots_dir)
        screenshot_path = screenshot_dir / f"{request.node.name}.png"
        browser_page.screenshot(path=str(screenshot_path), full_page=True)
        if allure is not None:
            allure.attach.file(str(screenshot_path), name=f"{request.node.name}-screenshot")

    browser_page.close()
