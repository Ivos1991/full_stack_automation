from __future__ import annotations

import os

import pytest
import requests

from src.api.clients.auth_client import AuthClient
from src.api.clients.comments_client import CommentsClient
from src.api.clients.notifications_client import NotificationsClient
from src.api.clients.test_data_client import TestDataClient
from src.api.clients.transactions_client import TransactionsClient
from src.api.clients.users_client import UsersClient
from src.api.schemas.auth_models import AuthCredentials
from src.api.schemas.comment_models import CommentCreatePayload, CommentRecord
from src.api.schemas.notification_models import NotificationRecord
from src.api.schemas.transaction_models import TransactionRecord
from src.api.schemas.user_models import CreatedUser, GeneratedUserData
from src.api.services.auth_service import AuthService
from src.api.services.comments_service import CommentsService
from src.api.services.notifications_service import NotificationsService
from src.api.services.test_data_service import TestDataService
from src.api.services.transactions_service import TransactionsService
from src.api.services.users_service import UsersService
from src.framework.config.settings import Settings


@pytest.fixture(scope="function")
def api_session() -> requests.Session:
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def auth_client(api_session: requests.Session, settings: Settings) -> AuthClient:
    return AuthClient(base_url=settings.api_base_url, session=api_session)


@pytest.fixture(scope="function")
def users_client(api_session: requests.Session, settings: Settings) -> UsersClient:
    return UsersClient(base_url=settings.api_base_url, session=api_session)


@pytest.fixture(scope="function")
def comments_client(api_session: requests.Session, settings: Settings) -> CommentsClient:
    return CommentsClient(base_url=settings.api_base_url, session=api_session)


@pytest.fixture(scope="function")
def notifications_client(api_session: requests.Session, settings: Settings) -> NotificationsClient:
    return NotificationsClient(base_url=settings.api_base_url, session=api_session)


@pytest.fixture(scope="function")
def transactions_client(api_session: requests.Session, settings: Settings) -> TransactionsClient:
    return TransactionsClient(base_url=settings.api_base_url, session=api_session)


@pytest.fixture(scope="function")
def test_data_client(api_session: requests.Session, settings: Settings) -> TestDataClient:
    return TestDataClient(base_url=settings.api_base_url, session=api_session)


@pytest.fixture(scope="function")
def auth_service(auth_client: AuthClient) -> AuthService:
    return AuthService(client=auth_client)


@pytest.fixture(scope="function")
def users_service(users_client: UsersClient) -> UsersService:
    return UsersService(client=users_client)


@pytest.fixture(scope="function")
def comments_service(comments_client: CommentsClient) -> CommentsService:
    return CommentsService(client=comments_client)


@pytest.fixture(scope="function")
def notifications_service(notifications_client: NotificationsClient) -> NotificationsService:
    return NotificationsService(client=notifications_client)


@pytest.fixture(scope="function")
def transactions_service(transactions_client: TransactionsClient) -> TransactionsService:
    return TransactionsService(client=transactions_client)


@pytest.fixture(scope="function")
def test_data_service(test_data_client: TestDataClient) -> TestDataService:
    return TestDataService(client=test_data_client)


@pytest.fixture(scope="function")
def seeded_user_credentials() -> AuthCredentials:
    return AuthCredentials(
        username=os.getenv("RWA_USERNAME", "Heath93"),
        password=os.getenv("RWA_PASSWORD", "s3cret"),
    )


@pytest.fixture(scope="function")
def authenticated_api_session(
    auth_service: AuthService,
    users_service: UsersService,
    seeded_user_credentials: AuthCredentials,
) -> requests.Session:
    auth_service.login(seeded_user_credentials)
    users_service.get_current_user()
    return auth_service.client.session


@pytest.fixture(scope="function")
def seeded_authenticated_api_session(
    auth_service: AuthService,
    users_service: UsersService,
    seeded_user_credentials: AuthCredentials,
) -> requests.Session:
    auth_service.login(seeded_user_credentials)
    users_service.get_current_user()
    return auth_service.client.session


@pytest.fixture(scope="function")
def created_user(
    test_data_service: TestDataService,
    users_service: UsersService,
    connected_users_repository,
    generated_user_data: GeneratedUserData,
) -> CreatedUser:
    test_data_service.seed_database()
    created_user_record = users_service.create_user(generated_user_data)

    persisted_user = connected_users_repository.get_user_by_username(created_user_record.username)
    if persisted_user is None:  # pragma: no cover - defensive guard
        raise RuntimeError(f"Expected created user {created_user_record.username} to exist in lowdb.")

    try:
        yield created_user_record
    finally:
        # Reset through the backend-supported testData route so the running app and lowdb file
        # return to the same seeded baseline after each test.
        test_data_service.seed_database()


@pytest.fixture(scope="function")
def seeded_sent_payment(
    seeded_business_data_state,
    auth_service: AuthService,
    transactions_service: TransactionsService,
    seeded_business_user_credentials: AuthCredentials,
    seeded_send_money_payment,
) -> TransactionRecord:
    auth_service.login(seeded_business_user_credentials)
    created_payment = transactions_service.create_payment(seeded_send_money_payment)
    return transactions_service.get_transaction_by_id(created_payment.id)


@pytest.fixture(scope="function")
def seeded_created_comment(
    seeded_business_data_state,
    auth_service: AuthService,
    comments_service: CommentsService,
    seeded_business_user_credentials: AuthCredentials,
    seeded_sent_payment: TransactionRecord,
    seeded_transaction_comment_payload: CommentCreatePayload,
) -> CommentRecord:
    auth_service.login(seeded_business_user_credentials)
    comments = comments_service.create_comment(
        transaction_id=seeded_sent_payment.id,
        payload=seeded_transaction_comment_payload,
    )
    matching_comment = next(
        (item for item in comments if item.content == seeded_transaction_comment_payload.content),
        None,
    )
    if matching_comment is None:  # pragma: no cover - defensive guard
        raise RuntimeError(
            f"Expected created comment {seeded_transaction_comment_payload.content} on transaction {seeded_sent_payment.id}."
        )
    return matching_comment


@pytest.fixture(scope="function")
def seeded_comment_notification(
    seeded_business_data_state,
    auth_service: AuthService,
    notifications_service: NotificationsService,
    seeded_created_comment: CommentRecord,
    seeded_send_money_contact_credentials: AuthCredentials,
) -> NotificationRecord | None:
    auth_service.login(seeded_send_money_contact_credentials)
    return notifications_service.get_unread_notification_for_transaction(
        seeded_created_comment.transaction_id,
        status="comment",
    )
