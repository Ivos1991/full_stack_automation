from __future__ import annotations
import pytest

@pytest.fixture(scope="function")
def persisted_receiver_comment_notification_comment(seeded_created_comment):
    """Expose the seeded comment that drives DB notification assertions."""
    return seeded_created_comment


@pytest.fixture(scope="function")
def persisted_receiver_comment_notification_receiver_user_id(seeded_send_money_contact) -> str:
    """Expose the receiver user id for local DB notification assertions."""
    return seeded_send_money_contact["id"]


@pytest.fixture(scope="function")
def persisted_receiver_comment_notification_unread(
    connected_notifications_repository,
    persisted_receiver_comment_notification_comment,
    persisted_receiver_comment_notification_receiver_user_id,
):
    """Resolve the receiver-side unread comment notification from lowdb before DB notification assertions."""
    return connected_notifications_repository.get_unread_comment_notification_by_user_and_transaction(
        user_id=persisted_receiver_comment_notification_receiver_user_id,
        transaction_id=persisted_receiver_comment_notification_comment.transaction_id,
    )
