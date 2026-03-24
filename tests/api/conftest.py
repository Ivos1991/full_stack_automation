from __future__ import annotations

import pytest


@pytest.fixture(scope="function")
def receiver_authenticated_notifications_service(
    auth_service,
    notifications_service,
    seeded_send_money_contact_credentials,
):
    """Authenticate as the receiver before notification API assertions so tests stay focused on behavior."""
    auth_service.login(seeded_send_money_contact_credentials)
    return notifications_service


@pytest.fixture(scope="function")
def receiver_comment_notification_comment(seeded_created_comment):
    """Expose the seeded comment used to create the receiver-side notification in API tests."""
    return seeded_created_comment


@pytest.fixture(scope="function")
def receiver_comment_notification_receiver_user_id(seeded_send_money_contact) -> str:
    """Expose the receiver user id for local API notification assertions."""
    return seeded_send_money_contact["id"]


@pytest.fixture(scope="function")
def receiver_comment_notification_unread(seeded_unread_comment_notification):
    """Expose the unread receiver-side comment notification for API transition assertions."""
    return seeded_unread_comment_notification
