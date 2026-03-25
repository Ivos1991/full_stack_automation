from __future__ import annotations
import pytest
from assertpy import assert_that, soft_assertions
from src.framework.reporting.evidence_helpers import attach_snapshot

@pytest.mark.integration
class TestTransactionCommentNotificationBackendIntegration:
    """Backend integration coverage for the transaction-comment notification lifecycle across API transitions and lowdb state."""

    def test_transaction_comment_notification_read_transition_expects_api_and_persistence_to_move_in_lockstep(
        self,
        require_live_rwa_environment,
        auth_service,
        notifications_service,
        connected_notifications_repository,
        integration_created_comment,
        integration_receiver_unread_comment_notification,
        seeded_send_money_contact,
        seeded_send_money_contact_credentials,
    ):
        """Create the transaction comment through the backend flow, load the receiver unread notification, mark it read, and confirm the persisted state change."""
        persisted_unread_before = connected_notifications_repository.get_notification_by_id(
            integration_receiver_unread_comment_notification.id
        )

        auth_service.login(seeded_send_money_contact_credentials)
        notifications_before = notifications_service.get_notifications()
        notifications_service.mark_notification_as_read(integration_receiver_unread_comment_notification.id)
        unread_after = notifications_service.get_unread_notification_for_transaction(
            integration_created_comment.transaction_id,
            status="comment",
        )
        notifications_after = notifications_service.get_notifications()
        persisted_notification_after = connected_notifications_repository.get_notification_by_id(
            integration_receiver_unread_comment_notification.id
        )

        attach_snapshot(
            name="transaction-comment-notification-backend-integration",
            comment=integration_created_comment,
            receiver_user_id=seeded_send_money_contact["id"],
            unread_before=integration_receiver_unread_comment_notification,
            persisted_unread_before=persisted_unread_before,
            notifications_before=notifications_before,
            unread_after=unread_after,
            notifications_after=notifications_after,
            persisted_notification_after=persisted_notification_after,
        )

        assert_that(
            persisted_unread_before,
            "Expected the unread comment notification to exist in lowdb before the backend read transition",
        ).is_not_none()
        assert_that(unread_after, "Expected no unread comment notification after the backend read transition").is_none()
        assert_that(
            persisted_notification_after,
            "Expected the same notification record to remain persisted after the read transition",
        ).is_not_none()

        with soft_assertions():
            assert_that(
                integration_receiver_unread_comment_notification.user_id,
                "The unread comment notification should belong to the receiver participant",
            ).is_equal_to(seeded_send_money_contact["id"])
            assert_that(
                integration_receiver_unread_comment_notification.transaction_id,
                "The unread comment notification should target the commented transaction",
            ).is_equal_to(integration_created_comment.transaction_id)
            assert_that(
                integration_receiver_unread_comment_notification.status,
                "The unread comment notification should normalize as a comment side effect",
            ).is_equal_to("comment")
            assert_that(
                integration_receiver_unread_comment_notification.is_read,
                "The notification should be unread before the backend transition",
            ).is_false()
            assert_that(
                len(notifications_before),
                "The receiver should have at least one unread notification before the backend read transition",
            ).is_greater_than(0)
            assert_that(
                len(notifications_after),
                "The receiver unread notification feed should shrink after marking the comment notification as read",
            ).is_less_than(len(notifications_before))
            assert_that(
                persisted_notification_after.id,
                "The persisted notification should still be the same record after the backend transition",
            ).is_equal_to(integration_receiver_unread_comment_notification.id)
            assert_that(
                persisted_notification_after.is_read,
                "The persisted notification should be marked read after the backend transition",
            ).is_true()
