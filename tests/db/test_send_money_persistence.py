from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.db
class TestSendMoneyPersistence:
    def test_seeded_user_send_money_persists_transaction_balance_and_notification(
        self,
        require_live_rwa_environment,
        auth_service,
        transactions_service,
        seeded_business_user_credentials,
        seeded_business_user,
        seeded_send_money_contact,
        seeded_send_money_payment,
        connected_users_repository,
        connected_transactions_repository,
        connected_notifications_repository,
    ):
        sender_before_payment = connected_users_repository.get_user_by_id(seeded_business_user["id"])
        receiver_before_payment = connected_users_repository.get_user_by_id(seeded_send_money_contact["id"])

        auth_service.login(seeded_business_user_credentials)
        created_payment = transactions_service.create_payment(seeded_send_money_payment)

        transaction_record = connected_transactions_repository.get_transaction_by_id(created_payment.id)
        sender_after_payment = connected_users_repository.get_user_by_id(seeded_business_user["id"])
        receiver_after_payment = connected_users_repository.get_user_by_id(seeded_send_money_contact["id"])
        payment_notification = connected_notifications_repository.get_unread_payment_notification_by_user_and_transaction(
            user_id=seeded_send_money_contact["id"],
            transaction_id=created_payment.id,
        )

        attach_json(
            name="seeded-send-money-db",
            content={
                "sender_before_payment": sender_before_payment,
                "receiver_before_payment": receiver_before_payment,
                "transaction_record": transaction_record.__dict__ if transaction_record else None,
                "sender_after_payment": sender_after_payment,
                "receiver_after_payment": receiver_after_payment,
                "payment_notification": payment_notification.__dict__ if payment_notification else None,
            },
        )

        assert_that(transaction_record, "Payment transaction should be persisted in lowdb").is_not_none()
        assert_that(
            payment_notification,
            "Receiver should have an unread payment notification for the created transaction",
        ).is_not_none()

        with soft_assertions():
            assert_that(transaction_record.sender_id, "Sender id persisted on transaction").is_equal_to(
                seeded_business_user["id"]
            )
            assert_that(transaction_record.receiver_id, "Receiver id persisted on transaction").is_equal_to(
                seeded_send_money_contact["id"]
            )
            assert_that(transaction_record.amount, "Persisted transaction amount should be in cents").is_equal_to(
                seeded_send_money_payment.amount_cents
            )
            assert_that(transaction_record.description, "Persisted transaction description should match").is_equal_to(
                seeded_send_money_payment.description
            )
            assert_that(transaction_record.status, "Persisted payment should be completed").is_equal_to("complete")
            assert_that(
                sender_after_payment["balance"],
                "Sender balance should be debited in lowdb after payment",
            ).is_equal_to(sender_before_payment["balance"] - seeded_send_money_payment.amount_cents)
            assert_that(
                receiver_after_payment["balance"],
                "Receiver balance should be credited in lowdb after payment",
            ).is_equal_to(receiver_before_payment["balance"] + seeded_send_money_payment.amount_cents)
            assert_that(
                payment_notification.status,
                "Receiver notification should record a received payment",
            ).is_equal_to("received")
            assert_that(
                payment_notification.is_read,
                "Receiver payment notification should remain unread immediately after creation",
            ).is_false()
