from __future__ import annotations

import re

from playwright.sync_api import expect

from src.ui.pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page, base_url: str) -> None:
        super().__init__(page=page, base_url=base_url)
        self.side_navigation_locator = self.page.locator("[data-test='sidenav']")
        self.transaction_list_locator = self.page.locator("[data-test='transaction-list']")
        self.sidenav_home_locator = self.page.locator("[data-test='sidenav-home']")
        self.sidenav_user_balance_locator = self.page.locator("[data-test='sidenav-user-balance']")
        self.new_transaction_button_locator = self.page.locator("[data-test='nav-top-new-transaction']")
        self.personal_tab_locator = self.page.locator("[data-test='nav-personal-tab']")
        self.user_onboarding_dialog_locator = self.page.locator("[data-test='user-onboarding-dialog']")
        self.user_onboarding_title_locator = self.page.locator("[data-test='user-onboarding-dialog-title']")

    def expect_home_feed_loaded(self) -> None:
        self.attach_current_url(name="home-page-url")
        expect(self.page).not_to_have_url(re.compile(r".*/signin/?$"))
        expect(self.side_navigation_locator).to_be_visible()
        expect(self.sidenav_home_locator).to_be_visible()
        expect(self.transaction_list_locator).to_be_visible()

    def expect_loaded(self) -> None:
        self.expect_home_feed_loaded()

    def expect_first_login_onboarding_loaded(self) -> None:
        self.attach_current_url(name="home-page-url")
        expect(self.page).not_to_have_url(re.compile(r".*/signin/?$"))
        expect(self.side_navigation_locator).to_be_visible()
        expect(self.user_onboarding_dialog_locator).to_be_visible()
        expect(self.user_onboarding_title_locator).to_contain_text("Get Started with Real World App")

    def expect_seeded_user_landing_loaded(self) -> None:
        self.attach_current_url(name="home-page-url")
        expect(self.page).not_to_have_url(re.compile(r".*/signin/?$"))
        expect(self.side_navigation_locator).to_be_visible()
        expect(self.sidenav_home_locator).to_be_visible()
        expect(self.transaction_list_locator).to_be_visible()
        expect(self.user_onboarding_dialog_locator).not_to_be_visible()

    def open_new_transaction(self) -> None:
        self.click(self.new_transaction_button_locator)
        expect(self.page).to_have_url(re.compile(r".*/transaction/new/?$"))

    def open_personal_feed(self) -> None:
        self.click(self.personal_tab_locator)
        expect(self.page).to_have_url(re.compile(r".*/personal/?$"))
        expect(self.transaction_list_locator).to_be_visible()

    def get_user_balance_text(self) -> str:
        expect(self.sidenav_user_balance_locator).to_be_visible()
        return self.sidenav_user_balance_locator.inner_text().strip()

    def expect_user_balance(self, expected_balance: str) -> None:
        expect(self.sidenav_user_balance_locator).to_have_text(expected_balance)

    def expect_transaction_with_description(self, description: str) -> None:
        matching_transaction_locator = self.page.locator("[data-test^='transaction-item-']").filter(has_text=description).first
        expect(matching_transaction_locator).to_be_visible()

    def open_transaction_with_description(self, description: str) -> None:
        matching_transaction_locator = self.page.locator("[data-test^='transaction-item-']").filter(has_text=description).first
        self.click(matching_transaction_locator)
        expect(self.page).to_have_url(re.compile(r".*/transaction/[^/]+/?$"))

    def get_visible_transaction_summaries(self, limit: int = 3) -> list[dict[str, str]]:
        self.transaction_list_locator.wait_for(state="visible")
        transaction_items = self.page.locator("[data-test^='transaction-item-']")
        count = min(transaction_items.count(), limit)
        summaries: list[dict[str, str]] = []

        for index in range(count):
            transaction_item = transaction_items.nth(index)
            transaction_id = transaction_item.get_attribute("data-test").removeprefix("transaction-item-")
            summaries.append(
                {
                    "id": transaction_id,
                    "sender_name": self.page.locator(f"[data-test='transaction-sender-{transaction_id}']").inner_text().strip(),
                    "action": self.page.locator(f"[data-test='transaction-action-{transaction_id}']").inner_text().strip(),
                    "receiver_name": self.page.locator(f"[data-test='transaction-receiver-{transaction_id}']").inner_text().strip(),
                    "amount_display": self.page.locator(f"[data-test='transaction-amount-{transaction_id}']").inner_text().strip(),
                }
            )

        return summaries
