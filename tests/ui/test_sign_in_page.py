from __future__ import annotations
from assertpy import assert_that
import pytest


@pytest.mark.ui
class TestSignInPage:
    """UI coverage for dynamic-user sign-in."""

    def test_dynamic_user_sign_in_expects_home_feed_loaded(
            self, require_live_rwa_environment, sign_in_page, home_page, auth_credentials):
        """Create a dynamic user through fixtures, sign in through the UI, and verify the first authenticated landing state."""
        sign_in_page.go_to()
        sign_in_page.sign_in(
            username=auth_credentials.username,
            password=auth_credentials.password
        )
        home_page.expect_first_login_onboarding_loaded()
        (assert_that(sign_in_page.page.url, "Expected authenticated browser URL")
         .is_equal_to("http://localhost:3000/"))
