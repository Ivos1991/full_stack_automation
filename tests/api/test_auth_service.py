from __future__ import annotations
from assertpy import assert_that
import pytest

@pytest.mark.api
class TestAuthService:
    """API coverage for dynamic-user authentication and current-user lookup."""

    def test_user_can_login_and_read_current_user_with_dynamic_credentials(
            self, require_live_rwa_environment, auth_service, users_service, auth_credentials, created_user):
        """Create a dynamic user through fixtures, then verify login and current-user retrieval for that account."""
        login_response = auth_service.login(auth_credentials)
        current_user = users_service.get_current_user()

        assert_that(login_response, "Expected login response payload").contains_key("user")
        assert_that(current_user.id, "Expected current user id").is_equal_to(created_user.id)
        assert_that(current_user.username, "Expected current username").is_equal_to(auth_credentials.username)
