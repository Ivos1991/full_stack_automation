from __future__ import annotations
import re
from playwright.sync_api import expect
from src.ui.pages.base_page import BasePage

class TransactionDetailPage(BasePage):
    def __init__(self, page, base_url: str) -> None:
        super().__init__(page=page, base_url=base_url)
        self.header_locator = self.page.locator("[data-test='transaction-detail-header']")
        self.description_locator = self.page.locator("[data-test='transaction-description']")
        self.sender_avatar_locator = self.page.locator("[data-test='transaction-sender-avatar']")
        self.receiver_avatar_locator = self.page.locator("[data-test='transaction-receiver-avatar']")
        self.comments_list_locator = self.page.locator("[data-test='comments-list']")

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(r".*/transaction/[^/]+/?$"))
        expect(self.header_locator).to_contain_text("Transaction Detail")

    def expect_amount(self, transaction_id: str, expected_amount: str) -> None:
        expect(self.page.locator(f"[data-test='transaction-amount-{transaction_id}']")).to_have_text(expected_amount)

    def expect_sender(self, transaction_id: str, expected_sender_name: str) -> None:
        expect(self.page.locator(f"[data-test='transaction-sender-{transaction_id}']")).to_have_text(expected_sender_name)
        expect(self.sender_avatar_locator).to_be_visible()

    def expect_receiver(self, transaction_id: str, expected_receiver_name: str) -> None:
        expect(self.page.locator(f"[data-test='transaction-receiver-{transaction_id}']")).to_have_text(expected_receiver_name)
        expect(self.receiver_avatar_locator).to_be_visible()

    def expect_description(self, expected_description: str) -> None:
        expect(self.description_locator).to_have_text(expected_description)

    def expect_status(self, transaction_id: str, expected_status_text: str) -> None:
        expect(self.page.locator(f"[data-test='transaction-action-{transaction_id}']")).to_contain_text(
            expected_status_text
        )

    def enter_comment(self, transaction_id: str, content: str) -> None:
        comment_input_locator = self.page.locator(f"[data-test='transaction-comment-input-{transaction_id}']")
        expect(comment_input_locator).to_be_visible()
        comment_input_locator.fill(content)

    def submit_comment(self, transaction_id: str) -> None:
        comment_input_locator = self.page.locator(f"[data-test='transaction-comment-input-{transaction_id}']")
        expect(comment_input_locator).to_be_visible()
        comment_input_locator.press("Enter")

    def add_comment(self, transaction_id: str, content: str) -> None:
        self.enter_comment(transaction_id=transaction_id, content=content)
        self.submit_comment(transaction_id=transaction_id)

    def expect_comment_displayed(self, content: str) -> None:
        expect(self.comments_list_locator).to_be_visible()
        expect(self.page.locator("[data-test^='comment-list-item-']").filter(has_text=content).first).to_be_visible()
