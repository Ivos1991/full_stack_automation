from __future__ import annotations
import pytest
from pathlib import Path
from assertpy import assert_that
from src.framework.reporting.allure_helpers import attach_file, attach_json

def _format_usd_from_cents(balance_cents: int) -> str:
    return f"${balance_cents / 100:,.2f}"


@pytest.mark.ui
class TestSeededSendMoneyPage:
    """UI coverage for the seeded send-money flow."""

    def test_seeded_send_money_flow_expects_success_confirmation_and_balance_update(
        self,
        require_live_rwa_environment,
        settings,
        sign_in_page,
        home_page,
        transaction_create_page,
        seeded_business_user,
        seeded_business_user_credentials,
        seeded_send_money_contact,
        seeded_send_money_payment,
    ):
        """Log in as the seeded sender, create a payment in the UI, and verify visible success and balance state."""
        expected_balance_after_payment = _format_usd_from_cents(
            seeded_business_user["balance"] - seeded_send_money_payment.amount_cents
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

        starting_balance = home_page.get_user_balance_text()
        home_page.open_new_transaction()

        transaction_create_page.expect_contact_selection_loaded()
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
            str(Path(settings.screenshots_dir) / "seeded-send-money-ui-success.png")
        )
        attach_file(path=screenshot_path, name="seeded-send-money-ui-success")

        transaction_create_page.return_to_transactions()
        home_page.open_personal_feed()
        home_page.expect_transaction_with_description(seeded_send_money_payment.description)
        home_page.expect_user_balance(expected_balance_after_payment)

        attach_json(
            name="seeded-send-money-ui",
            content={
                "starting_balance": starting_balance,
                "expected_balance_after_payment": expected_balance_after_payment,
                "recipient_username": seeded_send_money_contact["username"],
                "payment_description": seeded_send_money_payment.description,
            },
        )

        assert_that(starting_balance, "Expected the seeded sender to start with a visible balance").is_not_empty()
        assert_that(
            expected_balance_after_payment,
            "Expected the seeded sender balance after payment to be formatted",
        ).starts_with("$")
