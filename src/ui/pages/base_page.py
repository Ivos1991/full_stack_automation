from __future__ import annotations
from pathlib import Path
from playwright.sync_api import Locator, Page, expect
from src.framework.reporting.allure_helpers import attach_text

class BasePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self, path: str = "/") -> None:
        normalized_path = path if path.startswith("/") else f"/{path}"
        self.page.goto(f"{self.base_url}{normalized_path}")
        self.wait_for_page_ready()

    def open(self, path: str = "/") -> None:
        self.navigate(path)

    def set_default_timeout(self, timeout_ms: int) -> None:
        self.page.set_default_timeout(timeout_ms)

    def wait_for_page_ready(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        expect(self.page.locator("body")).to_be_visible()

    def click(self, locator: Locator) -> None:
        expect(locator).to_be_visible()
        locator.click()

    def fill(self, locator: Locator, value: str) -> None:
        expect(locator).to_be_visible()
        locator.fill(value)

    def type_text(self, locator: Locator, value: str) -> None:
        self.fill(locator, value)

    def attach_current_url(self, name: str = "page-url") -> None:
        attach_text(name=name, content=self.page.url)

    def screenshot(self, path: str) -> Path:
        screenshot_path = Path(path)
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(screenshot_path), full_page=True)
        return screenshot_path

    def expect_title_contains(self, expected_text: str) -> None:
        expect(self.page).to_have_title(expected_text)
