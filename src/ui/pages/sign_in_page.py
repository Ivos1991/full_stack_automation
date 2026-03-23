from __future__ import annotations

from playwright.sync_api import expect

from src.ui.pages.base_page import BasePage


class SignInPage(BasePage):
    PATH = "/signin"

    def __init__(self, page, base_url: str) -> None:
        super().__init__(page=page, base_url=base_url)
        self.username_input_locator = self.page.locator("[data-test='signin-username'] input")
        self.password_input_locator = self.page.locator("[data-test='signin-password'] input")
        self.submit_button_locator = self.page.locator("[data-test='signin-submit']")
        self.error_message_locator = self.page.locator("[data-test='signin-error']")

    def fill_in_username_and_password(self, username: str, password: str) -> None:
        self.fill(self.username_input_locator, username)
        self.fill(self.password_input_locator, password)

    def click_sign_in(self) -> None:
        self.click(self.submit_button_locator)

    def go_to(self) -> None:
        self.navigate(self.PATH)
        self.attach_current_url(name="sign-in-page-url")
        expect(self.submit_button_locator).to_be_visible()

    def sign_in(self, username: str, password: str) -> None:
        self.fill_in_username_and_password(username=username, password=password)
        self.click_sign_in()

    def expect_invalid_credentials_error(self) -> None:
        expect(self.error_message_locator).to_contain_text("Username or password is invalid")
