from __future__ import annotations

from assertpy import assert_that
import pytest


@pytest.mark.e2e
class TestSignInVerticalSlice:
    """End-to-end coverage for dynamic-user sign-in across UI, API, and lowdb state."""

    def test_sign_in_vertical_slice(
        self,
        require_live_rwa_environment,
        sign_in_page,
        home_page,
        auth_service,
        users_service,
        connected_users_repository,
        created_user,
        auth_credentials,
    ):
        """Create a dynamic user, sign in through the UI, then validate current-user API and persisted lowdb state."""
        # Validate the dynamically created lowdb-backed user exists before exercising the live app.
        db_user = connected_users_repository.get_user_by_username(auth_credentials.username)
        assert_that(db_user, "Expected created RWA user in lowdb data").is_not_none()
        assert_that(db_user["id"], "Expected DB user id").is_equal_to(created_user.id)
        assert_that(db_user["username"], "Expected DB username").is_equal_to(auth_credentials.username)

        # Validate the API auth and current-user contract.
        login_response = auth_service.login(auth_credentials)
        assert_that(login_response, "Expected login response payload").contains_key("user")

        current_user = users_service.get_current_user()
        assert_that(current_user.username, "Expected authenticated current user").is_equal_to(
            auth_credentials.username
        )

        # Validate the UI sign-in flow lands on the real first-login authenticated state.
        sign_in_page.go_to()
        sign_in_page.sign_in(auth_credentials.username, auth_credentials.password)
        home_page.expect_first_login_onboarding_loaded()
