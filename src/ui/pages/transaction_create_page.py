from __future__ import annotations
import re
from playwright.sync_api import expect
from src.ui.pages.base_page import BasePage

class TransactionCreatePage(BasePage):
    PATH = "/transaction/new"

    def __init__(self, page, base_url: str) -> None:
        super().__init__(page=page, base_url=base_url)
        self.user_list_search_input_locator = self.page.locator("[data-test='user-list-search-input']")
        self.users_list_locator = self.page.locator("[data-test='users-list']")
        self.amount_input_locator = self.page.locator("[data-test='transaction-create-amount-input'] input")
        self.description_input_locator = self.page.locator("[data-test='transaction-create-description-input'] input")
        self.submit_payment_button_locator = self.page.locator("[data-test='transaction-create-submit-payment']")
        self.success_alert_locator = self.page.locator("[data-test='alert-bar-success']")
        self.return_to_transactions_button_locator = self.page.locator(
            "[data-test='new-transaction-return-to-transactions']"
        )
        self.create_another_transaction_button_locator = self.page.locator(
            "[data-test='new-transaction-create-another-transaction']"
        )

    def go_to(self) -> None:
        self.navigate(self.PATH)
        self.expect_contact_selection_loaded()

    def expect_contact_selection_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(r".*/transaction/new/?$"))
        expect(self.user_list_search_input_locator).to_be_visible()
        expect(self.users_list_locator).to_be_visible()

    def search_contact(self, query: str) -> None:
        self.fill(self.user_list_search_input_locator, query)

    def select_contact_by_full_name(self, full_name: str) -> None:
        recipient_locator = self.page.locator("[data-test^='user-list-item-']").filter(has_text=full_name).first
        self.click(recipient_locator)

    def expect_payment_form_loaded(self, recipient_full_name: str) -> None:
        recipient_heading_locator = self.page.locator("h2").filter(has_text=recipient_full_name).first
        expect(recipient_heading_locator).to_be_visible()
        expect(self.amount_input_locator).to_be_visible()
        expect(self.description_input_locator).to_be_visible()
        expect(self.submit_payment_button_locator).to_be_visible()

    def enter_amount(self, amount: int) -> None:
        self.fill(self.amount_input_locator, str(amount))

    def enter_description(self, description: str) -> None:
        self.fill(self.description_input_locator, description)

    def submit_payment(self) -> None:
        self.click(self.submit_payment_button_locator)

    def expect_payment_success_state(self, amount_display: str, description: str) -> None:
        expect(self.success_alert_locator).to_contain_text("Transaction Submitted!")
        summary_locator = self.page.locator("h2").filter(has_text=f"Paid {amount_display} for {description}").first
        expect(summary_locator).to_be_visible()
        expect(self.return_to_transactions_button_locator).to_be_visible()
        expect(self.create_another_transaction_button_locator).to_be_visible()

    def return_to_transactions(self) -> None:
        self.click(self.return_to_transactions_button_locator)
        expect(self.page).to_have_url(re.compile(r".*/$"))
