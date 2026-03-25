from __future__ import annotations
import pytest

@pytest.fixture(scope="function")
def integration_created_payment(
    auth_service,
    transactions_service,
    seeded_business_user_credentials,
    seeded_send_money_payment,
):
    """Create one seeded payment through the real API so integration tests can share a backend-only source of truth."""
    auth_service.login(seeded_business_user_credentials)
    created_payment = transactions_service.create_payment(seeded_send_money_payment)
    return transactions_service.get_transaction_by_id(created_payment.id)


@pytest.fixture(scope="function")
def integration_created_comment(
    auth_service,
    comments_service,
    seeded_business_user_credentials,
    integration_created_payment,
    seeded_transaction_comment_payload,
):
    """Create one real transaction comment after the seeded payment so integration tests can validate the full side effect chain."""
    auth_service.login(seeded_business_user_credentials)
    comments = comments_service.create_comment(
        transaction_id=integration_created_payment.id,
        payload=seeded_transaction_comment_payload,
    )
    for item in comments:
        if item.content == seeded_transaction_comment_payload.content:
            return item
    raise RuntimeError(
        f"Expected created comment {seeded_transaction_comment_payload.content} on transaction {integration_created_payment.id}."
    )


@pytest.fixture(scope="function")
def integration_receiver_unread_comment_notification(
    auth_service,
    notifications_service,
    seeded_send_money_contact_credentials,
    integration_created_comment,
):
    """Authenticate as the receiver and load the unread comment notification before the read-state transition test starts."""
    auth_service.login(seeded_send_money_contact_credentials)
    notification = notifications_service.get_unread_notification_for_transaction(
        integration_created_comment.transaction_id,
        status="comment",
    )
    if notification is None:
        raise RuntimeError(
            f"Expected unread receiver notification for commented transaction {integration_created_comment.transaction_id}."
        )
    return notification
