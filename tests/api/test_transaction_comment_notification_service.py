from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.api
class TestTransactionCommentNotificationService:
    def test_transaction_comment_creates_unread_receiver_notification_via_api(
        self,
        require_live_rwa_environment,
        auth_service,
        notifications_service,
        seeded_created_comment,
        seeded_send_money_contact,
        seeded_send_money_contact_credentials,
    ):
        auth_service.login(seeded_send_money_contact_credentials)
        notification = notifications_service.get_unread_notification_for_transaction(
            seeded_created_comment.transaction_id,
            status="comment",
        )

        attach_json(
            name="transaction-comment-notification-api",
            content={
                "comment": seeded_created_comment.__dict__,
                "receiver_user_id": seeded_send_money_contact["id"],
                "notification": notification.__dict__ if notification else None,
            },
        )

        assert_that(notification, "Expected unread comment notification for the receiver via API").is_not_none()

        with soft_assertions():
            assert_that(
                notification.transaction_id,
                "Notification transaction id should match the commented transaction",
            ).is_equal_to(seeded_created_comment.transaction_id)
            assert_that(notification.user_id, "Notification should belong to the receiver").is_equal_to(
                seeded_send_money_contact["id"]
            )
            assert_that(notification.status, "Notification should represent a comment event").is_equal_to("comment")
            assert_that(
                notification.is_read,
                "New comment notification should remain unread immediately after creation",
            ).is_false()
