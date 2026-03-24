from __future__ import annotations
import pytest
from assertpy import assert_that
from src.framework.reporting.allure_helpers import attach_json

@pytest.mark.api
class TestTransactionsService:
    """API coverage for seeded transaction feed retrieval."""

    def test_seeded_public_feed_request_expects_transactions_in_api_response(
        self,
        require_live_rwa_environment,
        auth_service,
        transactions_service,
        seeded_business_user_credentials,
    ):
        """Authenticate as a seeded user and verify the public feed contract returns visible transactions."""
        auth_service.login(seeded_business_user_credentials)

        public_feed = transactions_service.get_public_feed(page=1, limit=10)
        attach_json(
            name="seeded-public-feed-api",
            content={
                "page_data": public_feed.page_data.__dict__,
                "first_result": public_feed.results[0].__dict__ if public_feed.results else None,
                "result_count": len(public_feed.results),
            },
        )

        assert_that(public_feed.page_data.page, "Expected public feed page").is_equal_to(1)
        assert_that(public_feed.page_data.limit, "Expected public feed limit").is_equal_to(10)
        assert_that(public_feed.results, "Expected seeded public feed results").is_not_empty()
        assert_that(public_feed.results[0].sender_name, "Expected first public feed sender").is_not_empty()
