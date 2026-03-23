from __future__ import annotations

from assertpy import assert_that
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.db
class TestTransactionsRepository:
    def test_seeded_user_public_feed_can_be_read_from_repository(
        self,
        require_live_rwa_environment,
        seeded_business_user,
        connected_transactions_repository,
    ):
        public_feed = connected_transactions_repository.get_public_feed_for_user(
            user_id=seeded_business_user["id"],
            page=1,
            limit=10,
        )
        attach_json(
            name="seeded-public-feed-db",
            content={
                "page_data": public_feed.page_data.__dict__,
                "first_result": public_feed.results[0].__dict__ if public_feed.results else None,
                "result_count": len(public_feed.results),
            },
        )

        assert_that(public_feed.page_data.page, "Expected repository feed page").is_equal_to(1)
        assert_that(public_feed.results, "Expected repository feed results").is_not_empty()
        assert_that(public_feed.results[0].id, "Expected first repository transaction id").is_not_empty()
