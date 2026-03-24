from __future__ import annotations
import pytest
from pathlib import Path
from assertpy import assert_that
from src.framework.reporting.allure_helpers import attach_file, attach_json

@pytest.mark.ui
class TestTransactionDetailPage:
    """UI coverage for opening and validating transaction detail."""

    def test_seeded_payment_detail_page_expects_amount_participants_description_and_status(
        self,
        require_live_rwa_environment,
        settings,
        sign_in_page,
        home_page,
        transaction_detail_page,
        seeded_business_user_credentials,
        seeded_sent_payment,
    ):
        """Reuse the fixture-created payment, navigate from the feed to detail, and verify the visible transaction fields."""
        sign_in_page.go_to()
        sign_in_page.sign_in(
            username=seeded_business_user_credentials.username,
            password=seeded_business_user_credentials.password,
        )
        home_page.expect_seeded_user_landing_loaded()
        home_page.open_personal_feed()
        home_page.open_transaction_with_description(seeded_sent_payment.description)

        transaction_detail_page.expect_loaded()
        transaction_detail_page.expect_sender(
            transaction_id=seeded_sent_payment.id,
            expected_sender_name=seeded_sent_payment.sender_name,
        )
        transaction_detail_page.expect_receiver(
            transaction_id=seeded_sent_payment.id,
            expected_receiver_name=seeded_sent_payment.receiver_name,
        )
        transaction_detail_page.expect_description(seeded_sent_payment.description)
        transaction_detail_page.expect_amount(
            transaction_id=seeded_sent_payment.id,
            expected_amount=seeded_sent_payment.signed_amount_display,
        )
        transaction_detail_page.expect_status(
            transaction_id=seeded_sent_payment.id,
            expected_status_text=seeded_sent_payment.action,
        )

        screenshot_path = transaction_detail_page.screenshot(
            str(Path(settings.screenshots_dir) / "transaction-detail-ui.png")
        )
        attach_file(path=screenshot_path, name="transaction-detail-ui")
        attach_json(name="transaction-detail-ui-source", content=seeded_sent_payment.__dict__)

        assert_that(
            seeded_sent_payment.id,
            "Expected the transaction-detail UI test to use the created payment as the source of truth",
        ).is_not_empty()
