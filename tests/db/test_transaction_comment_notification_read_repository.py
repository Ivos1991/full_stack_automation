from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.db
class TestTransactionCommentNotificationReadRepository:
    """DB coverage for the notification read-state transition triggered by a transaction comment."""

    def test_transaction_comment_notification_persists_read_state_after_transition(
        self,
        require_live_rwa_environment,
        auth_service,
        notifications_service,
        connected_notifications_repository,
        seeded_created_comment,
        seeded_send_money_contact,
        seeded_send_money_contact_credentials,
        seeded_unread_comment_notification,
    ):
        """Verify the unread receiver notification exists first, then patch it through the live API and assert lowdb stores it as read."""
        unread_before = connected_notifications_repository.get_unread_comment_notification_by_user_and_transaction(
            user_id=seeded_send_money_contact["id"],
            transaction_id=seeded_created_comment.transaction_id,
        )

        auth_service.login(seeded_send_money_contact_credentials)
        notifications_service.mark_notification_as_read(seeded_unread_comment_notification.id)

        unread_after = connected_notifications_repository.get_unread_comment_notification_by_user_and_transaction(
            user_id=seeded_send_money_contact["id"],
            transaction_id=seeded_created_comment.transaction_id,
        )
        persisted_notification = connected_notifications_repository.get_notification_by_id(
            seeded_unread_comment_notification.id
        )

        attach_json(
            name="transaction-comment-notification-read-db",
            content={
                "comment": seeded_created_comment.__dict__,
                "receiver_user_id": seeded_send_money_contact["id"],
                "unread_before": unread_before.__dict__ if unread_before else None,
                "unread_after": unread_after.__dict__ if unread_after else None,
                "persisted_notification": persisted_notification.__dict__ if persisted_notification else None,
            },
        )

        assert_that(unread_before, "Expected unread receiver notification before the read transition").is_not_none()
        assert_that(unread_after, "Expected no unread receiver comment notification after transition").is_none()
        assert_that(persisted_notification, "Expected the same notification record to remain in lowdb").is_not_none()

        with soft_assertions():
            assert_that(
                persisted_notification.id,
                "The persisted record should match the updated unread notification id",
            ).is_equal_to(seeded_unread_comment_notification.id)
            assert_that(persisted_notification.user_id, "Persisted notification should belong to the receiver").is_equal_to(
                seeded_send_money_contact["id"]
            )
            assert_that(
                persisted_notification.transaction_id,
                "Persisted notification should remain linked to the commented transaction",
            ).is_equal_to(seeded_created_comment.transaction_id)
            assert_that(
                persisted_notification.status,
                "Persisted notification should still normalize as a comment event",
            ).is_equal_to("comment")
            assert_that(
                persisted_notification.is_read,
                "Persisted notification should be marked read after the transition",
            ).is_true()
