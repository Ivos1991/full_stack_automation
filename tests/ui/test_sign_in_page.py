from __future__ import annotations
from assertpy import assert_that
import pytest


@pytest.mark.ui
class TestSignInPage:
    def test_user_can_sign_in_with_dynamic_credentials(
            self, require_live_rwa_environment, sign_in_page, home_page, auth_credentials):
        sign_in_page.go_to()
        sign_in_page.sign_in(
            username=auth_credentials.username,
            password=auth_credentials.password
        )
        home_page.expect_first_login_onboarding_loaded()
        (assert_that(sign_in_page.page.url, "Expected authenticated browser URL")
         .is_equal_to("http://localhost:3000/"))
