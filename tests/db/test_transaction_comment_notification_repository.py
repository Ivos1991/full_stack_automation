from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.db
class TestTransactionCommentNotificationRepository:
    """DB coverage for comment-triggered notification side effects."""

    def test_transaction_comment_notification_repository_query_expects_unread_receiver_notification(
        self,
        require_live_rwa_environment,
        persisted_receiver_comment_notification_comment,
        persisted_receiver_comment_notification_receiver_user_id,
        persisted_receiver_comment_notification_unread,
    ):
        """Create the comment through fixtures and verify the receiver-side unread notification in lowdb."""
        notification = persisted_receiver_comment_notification_unread

        attach_json(
            name="transaction-comment-notification-db",
            content={
                "comment": persisted_receiver_comment_notification_comment.__dict__,
                "receiver_user_id": persisted_receiver_comment_notification_receiver_user_id,
                "notification": notification.__dict__ if notification else None,
            },
        )

        assert_that(notification, "Expected persisted unread comment notification for the receiver").is_not_none()

        with soft_assertions():
            assert_that(
                notification.transaction_id,
                "Notification transaction id should match the commented transaction",
            ).is_equal_to(persisted_receiver_comment_notification_comment.transaction_id)
            assert_that(notification.user_id, "Notification should belong to the receiver").is_equal_to(
                persisted_receiver_comment_notification_receiver_user_id
            )
            assert_that(notification.status, "Notification should represent a comment event").is_equal_to("comment")
            assert_that(
                notification.is_read,
                "Persisted comment notification should remain unread immediately after creation",
            ).is_false()
