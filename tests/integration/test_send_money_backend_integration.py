from __future__ import annotations
import pytest
from assertpy import assert_that, soft_assertions
from src.framework.reporting.evidence_helpers import attach_snapshot

@pytest.mark.integration
class TestSendMoneyBackendIntegration:
    """Backend integration coverage for the seeded send-money business flow across API steps and persisted state."""

    def test_seeded_send_money_backend_flow_expects_endpoints_and_persistence_to_remain_aligned(
        self,
        require_live_rwa_environment,
        auth_service,
        users_service,
        transactions_service,
        connected_notifications_repository,
        connected_transactions_repository,
        connected_users_repository,
        seeded_business_user,
        seeded_send_money_contact,
        seeded_business_user_credentials,
        seeded_send_money_payment,
    ):
        """Create a seeded payment through the backend, validate follow-up endpoint behavior, and confirm the same result in lowdb."""
        auth_service.login(seeded_business_user_credentials)

        current_user_before_payment = users_service.get_current_user()
        created_payment = transactions_service.create_payment(seeded_send_money_payment)
        transaction_detail = transactions_service.get_transaction_by_id(created_payment.id)
        current_user_after_payment = users_service.get_current_user()
        personal_feed = transactions_service.get_personal_feed(page=1, limit=10)

        persisted_transaction = connected_transactions_repository.get_transaction_by_id(created_payment.id)
        persisted_sender = connected_users_repository.get_user_by_id(seeded_business_user["id"])
        persisted_receiver = connected_users_repository.get_user_by_id(seeded_send_money_contact["id"])
        persisted_receiver_notification = (
            connected_notifications_repository.get_unread_payment_notification_by_user_and_transaction(
                user_id=seeded_send_money_contact["id"],
                transaction_id=created_payment.id,
            )
        )

        expected_sender_balance_after_payment = seeded_business_user["balance"] - seeded_send_money_payment.amount_cents
        expected_receiver_balance_after_payment = seeded_send_money_contact["balance"] + seeded_send_money_payment.amount_cents

        attach_snapshot(
            name="send-money-backend-integration",
            current_user_before_payment=current_user_before_payment,
            created_payment=created_payment,
            transaction_detail=transaction_detail,
            current_user_after_payment=current_user_after_payment,
            first_personal_feed_item=personal_feed.results[0] if personal_feed.results else None,
            persisted_transaction=persisted_transaction,
            persisted_sender=persisted_sender,
            persisted_receiver=persisted_receiver,
            persisted_receiver_notification=persisted_receiver_notification,
        )

        assert_that(personal_feed.results, "Expected sender personal feed results after the backend payment flow").is_not_empty()
        assert_that(persisted_transaction, "Expected the created payment to persist in lowdb").is_not_none()
        assert_that(persisted_sender, "Expected the seeded sender record to remain available after the payment").is_not_none()
        assert_that(persisted_receiver, "Expected the seeded receiver record to remain available after the payment").is_not_none()
        assert_that(
            persisted_receiver_notification,
            "Expected the receiver unread payment notification after the backend payment flow",
        ).is_not_none()

        with soft_assertions():
            assert_that(created_payment.id, "Transaction detail should resolve the created backend payment").is_equal_to(
                transaction_detail.id
            )
            assert_that(created_payment.description, "The created payment should keep the seeded description").is_equal_to(
                seeded_send_money_payment.description
            )
            assert_that(created_payment.status, "The backend payment should complete immediately").is_equal_to("complete")
            assert_that(
                current_user_before_payment.balance,
                "Sender balance before the payment should match the seeded baseline",
            ).is_equal_to(seeded_business_user["balance"])
            assert_that(
                current_user_after_payment.balance,
                "Sender balance after the payment should be debited in the API read model",
            ).is_equal_to(expected_sender_balance_after_payment)
            assert_that(
                personal_feed.results[0].id,
                "The newest personal feed item should be the newly created backend payment",
            ).is_equal_to(created_payment.id)
            assert_that(
                persisted_transaction.id,
                "The persisted transaction should match the backend-created payment id",
            ).is_equal_to(created_payment.id)
            assert_that(
                persisted_transaction.sender_id,
                "The persisted transaction sender should remain the seeded business user",
            ).is_equal_to(seeded_business_user["id"])
            assert_that(
                persisted_transaction.receiver_id,
                "The persisted transaction receiver should remain the seeded contact",
            ).is_equal_to(seeded_send_money_contact["id"])
            assert_that(
                persisted_sender["balance"],
                "The persisted sender balance should match the debited API state",
            ).is_equal_to(expected_sender_balance_after_payment)
            assert_that(
                persisted_receiver["balance"],
                "The persisted receiver balance should reflect the credited payment amount",
            ).is_equal_to(expected_receiver_balance_after_payment)
            assert_that(
                persisted_receiver_notification.transaction_id,
                "The receiver notification should be linked to the created payment",
            ).is_equal_to(created_payment.id)
            assert_that(
                persisted_receiver_notification.is_read,
                "The receiver payment notification should be unread immediately after payment creation",
            ).is_false()
