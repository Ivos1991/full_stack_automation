from __future__ import annotations

from assertpy import assert_that
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.api
class TestSendMoneyService:
    def test_seeded_user_can_create_payment_and_observe_sender_api_state(
        self,
        require_live_rwa_environment,
        auth_service,
        users_service,
        transactions_service,
        seeded_business_user_credentials,
        seeded_business_user,
        seeded_send_money_contact,
        seeded_send_money_payment,
    ):
        auth_service.login(seeded_business_user_credentials)

        current_user_before_payment = users_service.get_current_user()
        created_payment = transactions_service.create_payment(seeded_send_money_payment)
        transaction_detail = transactions_service.get_transaction_by_id(created_payment.id)
        current_user_after_payment = users_service.get_current_user()
        personal_feed = transactions_service.get_personal_feed(page=1, limit=10)

        expected_balance_after_payment = seeded_business_user["balance"] - seeded_send_money_payment.amount_cents

        attach_json(
            name="seeded-send-money-api",
            content={
                "current_user_before_payment": current_user_before_payment.__dict__,
                "created_payment": created_payment.__dict__,
                "transaction_detail": transaction_detail.__dict__,
                "current_user_after_payment": current_user_after_payment.__dict__,
                "first_personal_feed_item": personal_feed.results[0].__dict__ if personal_feed.results else None,
            },
        )

        assert_that(
            created_payment.sender_id,
            "Created payment sender id should match the seeded sender",
        ).is_equal_to(seeded_business_user["id"])
        assert_that(
            created_payment.receiver_id,
            "Created payment receiver id should match the seeded contact",
        ).is_equal_to(seeded_send_money_contact["id"])
        assert_that(
            created_payment.description,
            "Created payment description should match the send-money payload",
        ).is_equal_to(seeded_send_money_payment.description)
        assert_that(created_payment.status, "Created payment status should be complete").is_equal_to("complete")
        assert_that(
            transaction_detail.id,
            "Transaction detail should resolve the created payment by id",
        ).is_equal_to(created_payment.id)
        assert_that(
            current_user_before_payment.balance,
            "Sender API balance before payment should match the seeded sender balance",
        ).is_equal_to(seeded_business_user["balance"])
        assert_that(
            current_user_after_payment.balance,
            "Sender API balance should be debited by the payment amount",
        ).is_equal_to(expected_balance_after_payment)
        assert_that(personal_feed.results, "Expected personal transaction feed results after payment").is_not_empty()
        assert_that(
            personal_feed.results[0].description,
            "Expected the newest personal transaction to be the created payment",
        ).is_equal_to(seeded_send_money_payment.description)
