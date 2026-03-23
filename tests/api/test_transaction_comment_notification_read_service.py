from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.api
class TestTransactionCommentNotificationReadService:
    """API coverage for the notification read-state transition triggered from a transaction comment."""

    def test_receiver_can_mark_transaction_comment_notification_as_read_via_api(
        self,
        require_live_rwa_environment,
        auth_service,
        notifications_service,
        seeded_created_comment,
        seeded_send_money_contact,
        seeded_send_money_contact_credentials,
        seeded_unread_comment_notification,
    ):
        """Load the unread receiver notification, update it through the real patch endpoint, and verify it leaves the unread feed."""
        auth_service.login(seeded_send_money_contact_credentials)
        unread_before = notifications_service.get_unread_notification_for_transaction(
            seeded_created_comment.transaction_id,
            status="comment",
        )
        notifications_service.mark_notification_as_read(seeded_unread_comment_notification.id)
        unread_after = notifications_service.get_unread_notification_for_transaction(
            seeded_created_comment.transaction_id,
            status="comment",
        )

        attach_json(
            name="transaction-comment-notification-read-api",
            content={
                "comment": seeded_created_comment.__dict__,
                "receiver_user_id": seeded_send_money_contact["id"],
                "unread_before": unread_before.__dict__ if unread_before else None,
                "unread_after": unread_after.__dict__ if unread_after else None,
            },
        )

        assert_that(unread_before, "Expected receiver unread comment notification before read transition").is_not_none()
        assert_that(unread_after, "Expected comment notification to disappear from unread API feed after transition").is_none()

        with soft_assertions():
            assert_that(unread_before.id, "The API transition should target the seeded unread notification").is_equal_to(
                seeded_unread_comment_notification.id
            )
            assert_that(unread_before.user_id, "Unread notification should belong to the receiver").is_equal_to(
                seeded_send_money_contact["id"]
            )
            assert_that(unread_before.status, "Unread notification should normalize as a comment event").is_equal_to(
                "comment"
            )
            assert_that(unread_before.is_read, "Unread notification should be unread before transition").is_false()
