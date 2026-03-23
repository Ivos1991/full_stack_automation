from __future__ import annotations

from src.ui.pages.login_page import LoginPage


class AuthFlow:
    def __init__(self, login_page: LoginPage) -> None:
        self.login_page = login_page

