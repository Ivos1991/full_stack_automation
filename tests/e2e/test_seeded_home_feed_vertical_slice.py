from __future__ import annotations
import pytest
from assertpy import assert_that
from src.framework.reporting.allure_helpers import attach_json

@pytest.mark.e2e
class TestSeededHomeFeedVerticalSlice:
    """End-to-end coverage for the seeded landing-feed slice across UI, API, and lowdb."""

    def test_seeded_home_feed_vertical_slice_expects_ui_api_and_db_alignment(
        self,
        require_live_rwa_environment,
        sign_in_page,
        home_page,
        auth_service,
        transactions_service,
        connected_transactions_repository,
        seeded_business_user,
        seeded_business_user_credentials,
    ):
        """Sign in as the seeded user, validate the visible feed, then confirm the same state through API and repository layers."""
        auth_service.login(seeded_business_user_credentials)
        api_feed = transactions_service.get_public_feed(page=1, limit=10)
        db_feed = connected_transactions_repository.get_public_feed_for_user(
            user_id=seeded_business_user["id"],
            page=1,
            limit=10,
        )

        sign_in_page.go_to()
        sign_in_page.sign_in(
            username=seeded_business_user_credentials.username,
            password=seeded_business_user_credentials.password,
        )
        home_page.expect_seeded_user_landing_loaded()
        ui_transactions = home_page.get_visible_transaction_summaries(limit=3)

        attach_json(name="seeded-home-feed-ui", content=ui_transactions)
        attach_json(name="seeded-home-feed-api", content=[item.__dict__ for item in api_feed.results[:3]])
        attach_json(name="seeded-home-feed-db", content=[item.__dict__ for item in db_feed.results[:3]])

        assert_that(api_feed.results, "Expected API seeded feed results").is_not_empty()
        assert_that(db_feed.results, "Expected DB seeded feed results").is_not_empty()
        assert_that(ui_transactions, "Expected UI seeded feed results").is_not_empty()

        first_api_item = api_feed.results[0]
        first_db_item = db_feed.results[0]
        first_ui_item = ui_transactions[0]

        assert_that(first_db_item.id, "Expected DB and API first transaction id to match").is_equal_to(
            first_api_item.id
        )
        assert_that(first_ui_item["id"], "Expected UI and API first transaction id to match").is_equal_to(
            first_api_item.id
        )
        assert_that(first_ui_item["sender_name"], "Expected UI sender to match API sender").is_equal_to(
            first_api_item.sender_name
        )
        assert_that(first_ui_item["receiver_name"], "Expected UI receiver to match API receiver").is_equal_to(
            first_api_item.receiver_name
        )
        assert_that(first_ui_item["amount_display"], "Expected UI amount to match API amount").is_equal_to(
            first_api_item.amount_display
        )
