from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.api
class TestTransactionCommentNotificationReadService:
    """API coverage for the notification read-state transition triggered from a transaction comment."""

    def test_notification_read_transition_expects_comment_notification_removed_from_unread_api_feed(
        self,
        require_live_rwa_environment,
        receiver_authenticated_notifications_service,
        receiver_comment_notification_comment,
        receiver_comment_notification_receiver_user_id,
        receiver_comment_notification_unread,
    ):
        """Load the unread receiver notification, update it through the real patch endpoint, and verify it leaves the unread feed."""
        unread_before = next(
            (
                item
                for item in receiver_authenticated_notifications_service.get_notifications()
                if item.id == receiver_comment_notification_unread.id
            ),
            None,
        )
        receiver_authenticated_notifications_service.mark_notification_as_read(
            receiver_comment_notification_unread.id
        )
        unread_after = receiver_authenticated_notifications_service.get_unread_notification_for_transaction(
            receiver_comment_notification_comment.transaction_id,
            status="comment",
        )

        attach_json(
            name="transaction-comment-notification-read-api",
            content={
                "comment": receiver_comment_notification_comment.__dict__,
                "receiver_user_id": receiver_comment_notification_receiver_user_id,
                "unread_before": unread_before.__dict__ if unread_before else None,
                "unread_after": unread_after.__dict__ if unread_after else None,
            },
        )

        assert_that(unread_before, "Expected receiver unread comment notification before read transition").is_not_none()
        assert_that(unread_after, "Expected comment notification to disappear from unread API feed after transition").is_none()

        with soft_assertions():
            assert_that(unread_before.id, "The API transition should target the seeded unread notification").is_equal_to(
                receiver_comment_notification_unread.id
            )
            assert_that(unread_before.user_id, "Unread notification should belong to the receiver").is_equal_to(
                receiver_comment_notification_receiver_user_id
            )
            assert_that(unread_before.status, "Unread notification should normalize as a comment event").is_equal_to(
                "comment"
            )
            assert_that(unread_before.is_read, "Unread notification should be unread before transition").is_false()
