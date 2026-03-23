from __future__ import annotations

import pytest

from src.db.repositories.comments_repository import CommentsRepository
from src.db.repositories.contacts_repository import ContactsRepository
from src.db.repositories.notifications_repository import NotificationsRepository
from src.db.repositories.users_repository import UsersRepository
from src.db.repositories.transactions_repository import TransactionsRepository
from src.framework.clients.db.lowdb_json_client import LowDBJSONClient
from src.framework.config.settings import Settings


@pytest.fixture(scope="function")
def db_client(settings: Settings) -> LowDBJSONClient:
    return LowDBJSONClient(data_file=settings.rwa_data_file)


@pytest.fixture(scope="function")
def connected_db_client(db_client: LowDBJSONClient) -> LowDBJSONClient:
    """Open the lowdb file for the test and close the client during teardown."""
    db_client.connect()
    yield db_client
    db_client.close()


@pytest.fixture(scope="function")
def users_repository(db_client: LowDBJSONClient) -> UsersRepository:
    return UsersRepository(db_client=db_client)


@pytest.fixture(scope="function")
def connected_users_repository(connected_db_client: LowDBJSONClient) -> UsersRepository:
    return UsersRepository(db_client=connected_db_client)


@pytest.fixture(scope="function")
def contacts_repository(db_client: LowDBJSONClient) -> ContactsRepository:
    return ContactsRepository(db_client=db_client)


@pytest.fixture(scope="function")
def connected_contacts_repository(connected_db_client: LowDBJSONClient) -> ContactsRepository:
    return ContactsRepository(db_client=connected_db_client)


@pytest.fixture(scope="function")
def comments_repository(db_client: LowDBJSONClient) -> CommentsRepository:
    return CommentsRepository(db_client=db_client)


@pytest.fixture(scope="function")
def connected_comments_repository(connected_db_client: LowDBJSONClient) -> CommentsRepository:
    return CommentsRepository(db_client=connected_db_client)


@pytest.fixture(scope="function")
def transactions_repository(db_client: LowDBJSONClient) -> TransactionsRepository:
    return TransactionsRepository(db_client=db_client)


@pytest.fixture(scope="function")
def connected_transactions_repository(connected_db_client: LowDBJSONClient) -> TransactionsRepository:
    return TransactionsRepository(db_client=connected_db_client)


@pytest.fixture(scope="function")
def notifications_repository(db_client: LowDBJSONClient) -> NotificationsRepository:
    return NotificationsRepository(db_client=db_client)


@pytest.fixture(scope="function")
def connected_notifications_repository(connected_db_client: LowDBJSONClient) -> NotificationsRepository:
    return NotificationsRepository(db_client=connected_db_client)
