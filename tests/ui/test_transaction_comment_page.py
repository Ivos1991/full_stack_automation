from __future__ import annotations

from pathlib import Path

from assertpy import assert_that
import pytest

from src.framework.reporting.allure_helpers import attach_file, attach_json


@pytest.mark.ui
class TestTransactionCommentPage:
    """UI coverage for transaction-detail comment creation."""

    def test_seeded_sent_payment_can_receive_comment_in_transaction_detail_ui(
        self,
        require_live_rwa_environment,
        settings,
        sign_in_page,
        home_page,
        transaction_detail_page,
        seeded_business_user_credentials,
        seeded_sent_payment,
        seeded_transaction_comment_payload,
    ):
        """Open the seeded transaction detail, create a comment, and verify the comment renders in the UI."""
        sign_in_page.go_to()
        sign_in_page.sign_in(
            username=seeded_business_user_credentials.username,
            password=seeded_business_user_credentials.password,
        )
        home_page.expect_seeded_user_landing_loaded()
        home_page.open_personal_feed()
        home_page.open_transaction_with_description(seeded_sent_payment.description)

        transaction_detail_page.expect_loaded()
        transaction_detail_page.add_comment(
            transaction_id=seeded_sent_payment.id,
            content=seeded_transaction_comment_payload.content,
        )
        transaction_detail_page.expect_comment_displayed(seeded_transaction_comment_payload.content)

        screenshot_path = transaction_detail_page.screenshot(
            str(Path(settings.screenshots_dir) / "transaction-detail-comment-ui.png")
        )
        attach_file(path=screenshot_path, name="transaction-detail-comment-ui")
        attach_json(
            name="transaction-detail-comment-ui",
            content={
                "transaction": seeded_sent_payment.__dict__,
                "comment_content": seeded_transaction_comment_payload.content,
            },
        )

        assert_that(
            seeded_transaction_comment_payload.content,
            "Expected comment content for transaction-detail UI test",
        ).is_not_empty()
