from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.e2e
class TestTransactionCommentNotificationVerticalSlice:
    """End-to-end coverage for the notification side effect triggered by a transaction comment."""

    def test_transaction_comment_creates_unread_receiver_notification_across_api_and_db(
        self,
        require_live_rwa_environment,
        auth_service,
        notifications_service,
        connected_notifications_repository,
        seeded_send_money_contact,
        seeded_send_money_contact_credentials,
        ui_created_transaction_comment_record,
        ui_created_transaction_comment_transaction,
    ):
        """Create the payment and comment in the UI, then verify the receiver-side unread notification through API and DB."""
        auth_service.login(seeded_send_money_contact_credentials)
        api_notification = notifications_service.get_unread_notification_for_transaction(
            ui_created_transaction_comment_transaction.id,
            status="comment",
        )
        db_notification = connected_notifications_repository.get_unread_comment_notification_by_user_and_transaction(
            user_id=seeded_send_money_contact["id"],
            transaction_id=ui_created_transaction_comment_transaction.id,
        )

        attach_json(
            name="transaction-comment-notification-e2e",
            content={
                "transaction": ui_created_transaction_comment_transaction.__dict__,
                "comment": ui_created_transaction_comment_record.__dict__,
                "api_notification": api_notification.__dict__ if api_notification else None,
                "db_notification": db_notification.__dict__ if db_notification else None,
            },
        )

        assert_that(
            api_notification,
            "Expected unread comment notification in API state after UI comment creation",
        ).is_not_none()
        assert_that(
            db_notification,
            "Expected unread comment notification in DB state after UI comment creation",
        ).is_not_none()

        with soft_assertions():
            assert_that(api_notification.user_id, "API notification should belong to the receiver").is_equal_to(
                seeded_send_money_contact["id"]
            )
            assert_that(
                api_notification.transaction_id,
                "API notification transaction id should match",
            ).is_equal_to(ui_created_transaction_comment_transaction.id)
            assert_that(api_notification.status, "API notification should represent a comment event").is_equal_to(
                "comment"
            )
            assert_that(
                api_notification.is_read,
                "API notification should remain unread immediately after creation",
            ).is_false()
            assert_that(db_notification.user_id, "DB notification should belong to the receiver").is_equal_to(
                seeded_send_money_contact["id"]
            )
            assert_that(
                db_notification.transaction_id,
                "DB notification transaction id should match",
            ).is_equal_to(ui_created_transaction_comment_transaction.id)
            assert_that(db_notification.status, "DB notification should represent a comment event").is_equal_to(
                "comment"
            )
            assert_that(
                db_notification.is_read,
                "DB notification should remain unread immediately after creation",
            ).is_false()
