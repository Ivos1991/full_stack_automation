from __future__ import annotations

from pathlib import Path

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_file, attach_json


@pytest.mark.e2e
class TestTransactionDetailVerticalSlice:
    """End-to-end coverage for transaction-detail validation after a seeded payment is created."""

    def test_transaction_detail_vertical_slice_expects_ui_api_and_db_alignment(
        self,
        require_live_rwa_environment,
        settings,
        sign_in_page,
        home_page,
        transaction_create_page,
        transaction_detail_page,
        auth_service,
        transactions_service,
        connected_transactions_repository,
        seeded_business_user,
        seeded_business_user_credentials,
        seeded_send_money_contact,
        seeded_send_money_payment,
    ):
        """Create a payment in the UI, open its detail page, and validate the same transaction through UI, API, and DB."""
        recipient_full_name = (
            f"{seeded_send_money_contact['firstName']} {seeded_send_money_contact['lastName']}"
        )

        sign_in_page.go_to()
        sign_in_page.sign_in(
            username=seeded_business_user_credentials.username,
            password=seeded_business_user_credentials.password,
        )
        home_page.expect_seeded_user_landing_loaded()
        home_page.open_new_transaction()

        transaction_create_page.search_contact(seeded_send_money_contact["firstName"])
        transaction_create_page.select_contact_by_full_name(recipient_full_name)
        transaction_create_page.expect_payment_form_loaded(recipient_full_name=recipient_full_name)
        transaction_create_page.enter_amount(seeded_send_money_payment.amount)
        transaction_create_page.enter_description(seeded_send_money_payment.description)
        transaction_create_page.submit_payment()
        transaction_create_page.expect_payment_success_state(
            amount_display=seeded_send_money_payment.amount_display,
            description=seeded_send_money_payment.description,
        )
        transaction_create_page.return_to_transactions()

        home_page.open_personal_feed()
        home_page.open_transaction_with_description(seeded_send_money_payment.description)

        persisted_transaction = connected_transactions_repository.get_latest_payment_by_participants_and_description(
            sender_id=seeded_business_user["id"],
            receiver_id=seeded_send_money_contact["id"],
            description=seeded_send_money_payment.description,
        )
        assert_that(
            persisted_transaction,
            "UI-created payment should be resolvable from the repository before detail validation",
        ).is_not_none()

        transaction_detail_page.expect_loaded()
        transaction_detail_page.expect_sender(
            transaction_id=persisted_transaction.id,
            expected_sender_name=persisted_transaction.sender_name,
        )
        transaction_detail_page.expect_receiver(
            transaction_id=persisted_transaction.id,
            expected_receiver_name=persisted_transaction.receiver_name,
        )
        transaction_detail_page.expect_description(persisted_transaction.description)
        transaction_detail_page.expect_amount(
            transaction_id=persisted_transaction.id,
            expected_amount=persisted_transaction.signed_amount_display,
        )
        transaction_detail_page.expect_status(
            transaction_id=persisted_transaction.id,
            expected_status_text=persisted_transaction.action,
        )

        screenshot_path = transaction_detail_page.screenshot(
            str(Path(settings.screenshots_dir) / "transaction-detail-e2e.png")
        )
        attach_file(path=screenshot_path, name="transaction-detail-e2e")

        auth_service.login(seeded_business_user_credentials)
        api_transaction = transactions_service.get_transaction_by_id(persisted_transaction.id)

        attach_json(
            name="transaction-detail-e2e",
            content={
                "ui_transaction": persisted_transaction.__dict__,
                "api_transaction": api_transaction.__dict__,
                "db_transaction": persisted_transaction.__dict__,
            },
        )

        with soft_assertions():
            assert_that(api_transaction.id, "API detail id should match the UI-created transaction id").is_equal_to(
                persisted_transaction.id
            )
            assert_that(api_transaction.description, "API detail description should match").is_equal_to(
                persisted_transaction.description
            )
            assert_that(api_transaction.amount, "API detail amount should match").is_equal_to(
                persisted_transaction.amount
            )
            assert_that(api_transaction.sender_id, "API detail sender id should match").is_equal_to(
                persisted_transaction.sender_id
            )
            assert_that(api_transaction.receiver_id, "API detail receiver id should match").is_equal_to(
                persisted_transaction.receiver_id
            )
            assert_that(api_transaction.status, "API detail status should remain complete").is_equal_to("complete")
