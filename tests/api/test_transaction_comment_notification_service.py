from __future__ import annotations
import pytest
from assertpy import assert_that, soft_assertions
from src.framework.reporting.allure_helpers import attach_json

@pytest.mark.api
class TestTransactionCommentNotificationService:
    """API coverage for notification side effects triggered by transaction comments."""

    def test_transaction_comment_notification_feed_expects_unread_receiver_notification(
        self,
        require_live_rwa_environment,
        receiver_authenticated_notifications_service,
        receiver_comment_notification_comment,
        receiver_comment_notification_receiver_user_id,
        receiver_comment_notification_unread,
    ):
        """Create the comment through setup fixtures, then authenticate as the receiver and verify the unread notification."""
        notification = next(
            (
                item
                for item in receiver_authenticated_notifications_service.get_notifications()
                if item.id == receiver_comment_notification_unread.id
            ),
            None,
        )

        attach_json(
            name="transaction-comment-notification-api",
            content={
                "comment": receiver_comment_notification_comment.__dict__,
                "receiver_user_id": receiver_comment_notification_receiver_user_id,
                "notification": notification.__dict__ if notification else None,
            },
        )

        assert_that(notification, "Expected unread comment notification for the receiver via API").is_not_none()

        with soft_assertions():
            assert_that(
                notification.transaction_id,
                "Notification transaction id should match the commented transaction",
            ).is_equal_to(receiver_comment_notification_comment.transaction_id)
            assert_that(notification.user_id, "Notification should belong to the receiver").is_equal_to(
                receiver_comment_notification_receiver_user_id
            )
            assert_that(notification.status, "Notification should represent a comment event").is_equal_to("comment")
            assert_that(
                notification.is_read,
                "New comment notification should remain unread immediately after creation",
            ).is_false()
