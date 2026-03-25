from __future__ import annotations
import pytest
from assertpy import assert_that
from src.framework.reporting.evidence_helpers import attach_snapshot

@pytest.mark.ui
class TestSeededHomeFeed:
    """UI coverage for the seeded user's authenticated landing feed."""

    def test_seeded_user_home_feed_expects_transaction_list_loaded(
        self,
        require_live_rwa_environment,
        sign_in_page,
        home_page,
        seeded_business_user_credentials,
    ):
        """Sign in as the seeded user and verify the transaction feed renders after the UI login flow."""
        sign_in_page.go_to()
        sign_in_page.sign_in(
            username=seeded_business_user_credentials.username,
            password=seeded_business_user_credentials.password,
        )

        home_page.expect_seeded_user_landing_loaded()
        visible_transactions = home_page.get_visible_transaction_summaries(limit=3)
        attach_snapshot(name="seeded-home-feed-ui-transactions", content=visible_transactions)

        assert_that(visible_transactions, "Expected visible seeded home feed transactions").is_not_empty()
        assert_that(visible_transactions[0], "Expected first visible transaction summary").contains_key(
            "id",
            "sender_name",
            "action",
            "receiver_name",
            "amount_display",
        )
