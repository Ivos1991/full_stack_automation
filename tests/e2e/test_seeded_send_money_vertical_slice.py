from __future__ import annotations
import pytest
from pathlib import Path
from assertpy import assert_that, soft_assertions
from src.framework.reporting.allure_helpers import attach_file, attach_json

def _format_usd_from_cents(balance_cents: int) -> str:
    return f"${balance_cents / 100:,.2f}"


@pytest.mark.e2e
class TestSeededSendMoneyVerticalSlice:
    """End-to-end coverage for the seeded send-money slice across UI, API, and lowdb."""

    def test_seeded_send_money_vertical_slice_expects_ui_api_and_db_alignment(
        self,
        require_live_rwa_environment,
        settings,
        sign_in_page,
        home_page,
        transaction_create_page,
        auth_service,
        users_service,
        transactions_service,
        connected_users_repository,
        connected_transactions_repository,
        connected_notifications_repository,
        seeded_business_user,
        seeded_business_user_credentials,
        seeded_send_money_contact,
        seeded_send_money_payment,
    ):
        """Create a payment in the UI, then validate the resulting transaction, balances, and notification through API and DB."""
        expected_sender_balance_after_payment = seeded_business_user["balance"] - seeded_send_money_payment.amount_cents
        expected_sender_balance_text = _format_usd_from_cents(expected_sender_balance_after_payment)
        expected_receiver_balance_after_payment = (
            seeded_send_money_contact["balance"] + seeded_send_money_payment.amount_cents
        )
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

        screenshot_path = transaction_create_page.screenshot(
            str(Path(settings.screenshots_dir) / "seeded-send-money-e2e-success.png")
        )
        attach_file(path=screenshot_path, name="seeded-send-money-e2e-success")

        transaction_create_page.return_to_transactions()
        home_page.open_personal_feed()
        home_page.expect_transaction_with_description(seeded_send_money_payment.description)
        home_page.expect_user_balance(expected_sender_balance_text)

        auth_service.login(seeded_business_user_credentials)
        persisted_transaction = connected_transactions_repository.get_latest_payment_by_participants_and_description(
            sender_id=seeded_business_user["id"],
            receiver_id=seeded_send_money_contact["id"],
            description=seeded_send_money_payment.description,
        )
        assert_that(
            persisted_transaction,
            "UI-created payment should be discoverable in the lowdb repository",
        ).is_not_none()

        api_transaction = transactions_service.get_transaction_by_id(persisted_transaction.id)
        api_current_user = users_service.get_current_user()
        db_sender_after_payment = connected_users_repository.get_user_by_id(seeded_business_user["id"])
        db_receiver_after_payment = connected_users_repository.get_user_by_id(seeded_send_money_contact["id"])
        db_receiver_notification = connected_notifications_repository.get_unread_payment_notification_by_user_and_transaction(
            user_id=seeded_send_money_contact["id"],
            transaction_id=persisted_transaction.id,
        )

        attach_json(
            name="seeded-send-money-e2e",
            content={
                "ui": {
                    "expected_sender_balance_text": expected_sender_balance_text,
                    "payment_description": seeded_send_money_payment.description,
                    "recipient_username": seeded_send_money_contact["username"],
                },
                "api_transaction": api_transaction.__dict__,
                "api_current_user": api_current_user.__dict__,
                "db_transaction": persisted_transaction.__dict__ if persisted_transaction else None,
                "db_sender_after_payment": db_sender_after_payment,
                "db_receiver_after_payment": db_receiver_after_payment,
                "db_receiver_notification": db_receiver_notification.__dict__ if db_receiver_notification else None,
            },
        )

        assert_that(
            db_receiver_notification,
            "UI-created payment should create an unread receiver notification in lowdb",
        ).is_not_none()

        with soft_assertions():
            assert_that(api_transaction.id, "API transaction id should match the persisted transaction id").is_equal_to(
                persisted_transaction.id
            )
            assert_that(
                api_transaction.description,
                "API transaction description should match the UI-created payment",
            ).is_equal_to(seeded_send_money_payment.description)
            assert_that(
                api_current_user.balance,
                "API current-user balance should match the expected sender balance after payment",
            ).is_equal_to(expected_sender_balance_after_payment)
            assert_that(
                db_sender_after_payment["balance"],
                "DB sender balance should match the expected sender balance after payment",
            ).is_equal_to(expected_sender_balance_after_payment)
            assert_that(
                db_receiver_after_payment["balance"],
                "DB receiver balance should be credited by the payment amount",
            ).is_equal_to(expected_receiver_balance_after_payment)
            assert_that(
                db_receiver_notification.status,
                "DB receiver notification should record a received payment",
            ).is_equal_to("received")
