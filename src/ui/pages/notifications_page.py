from __future__ import annotations

import re

from playwright.sync_api import expect

from src.ui.pages.base_page import BasePage


class NotificationsPage(BasePage):
    PATH = "/notifications"

    def __init__(self, page, base_url: str) -> None:
        super().__init__(page=page, base_url=base_url)
        self.notifications_list_locator = self.page.locator("[data-test='notifications-list']")

    def go_to(self) -> None:
        self.navigate(self.PATH)
        self.expect_loaded()

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(r".*/notifications/?$"))

    def expect_notification_visible(self, notification_id: str, expected_text: str) -> None:
        notification_locator = self.page.locator(f"[data-test='notification-list-item-{notification_id}']")
        expect(notification_locator).to_be_visible()
        expect(notification_locator).to_contain_text(expected_text)

    def dismiss_notification(self, notification_id: str) -> None:
        dismiss_button = self.page.locator(f"[data-test='notification-mark-read-{notification_id}']")
        expect(dismiss_button).to_be_visible()
        dismiss_button.click()

    def expect_notification_absent(self, notification_id: str) -> None:
        expect(self.page.locator(f"[data-test='notification-list-item-{notification_id}']")).to_have_count(0)
