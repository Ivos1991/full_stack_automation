from __future__ import annotations
import os
import pytest
import requests
from assertpy import assert_that
from src.framework.config.settings import Settings
from src.api.schemas.auth_models import AuthCredentials

@pytest.fixture(scope="function")
def sign_in_page(page, settings: Settings):
    try:
        from src.ui.pages.sign_in_page import SignInPage
    except ImportError as error:  # pragma: no cover - depends on local environment
        pytest.skip(f"Playwright UI dependencies are unavailable: {error}")

    return SignInPage(page=page, base_url=settings.base_url)


@pytest.fixture(scope="function")
def home_page(page, settings: Settings):
    try:
        from src.ui.pages.home_page import HomePage
    except ImportError as error:  # pragma: no cover - depends on local environment
        pytest.skip(f"Playwright UI dependencies are unavailable: {error}")

    return HomePage(page=page, base_url=settings.base_url)


@pytest.fixture(scope="function")
def transaction_create_page(page, settings: Settings):
    try:
        from src.ui.pages.transaction_create_page import TransactionCreatePage
    except ImportError as error:  # pragma: no cover - depends on local environment
        pytest.skip(f"Playwright UI dependencies are unavailable: {error}")

    return TransactionCreatePage(page=page, base_url=settings.base_url)


@pytest.fixture(scope="function")
def transaction_detail_page(page, settings: Settings):
    try:
        from src.ui.pages.transaction_detail_page import TransactionDetailPage
    except ImportError as error:  # pragma: no cover - depends on local environment
        pytest.skip(f"Playwright UI dependencies are unavailable: {error}")

    return TransactionDetailPage(page=page, base_url=settings.base_url)


@pytest.fixture(scope="function")
def notifications_page(page, settings: Settings):
    try:
        from src.ui.pages.notifications_page import NotificationsPage
    except ImportError as error:  # pragma: no cover - depends on local environment
        pytest.skip(f"Playwright UI dependencies are unavailable: {error}")

    return NotificationsPage(page=page, base_url=settings.base_url)


@pytest.fixture(scope="function")
def require_live_rwa_environment(settings: Settings, db_client) -> None:
    """Verify the external RWA frontend, backend, and lowdb file are reachable for the test, then close the DB client."""
    try:
        sign_in_response = requests.get(f"{settings.base_url}/signin", timeout=5)
        login_response = requests.post(
            f"{settings.api_base_url}/login",
            json={"username": "health-check", "password": "health-check"},
            timeout=5,
        )

        if sign_in_response.status_code >= 400:
            pytest.skip(f"Expected RWA sign-in page is not available at {settings.base_url}/signin")

        if login_response.status_code in {404, 405}:
            pytest.skip(f"Expected RWA login endpoint is not available at {settings.api_base_url}/login")

        connected_client = db_client.connect()
        assert_that(connected_client, "Expected lowdb client to load data").is_not_none()
    except Exception as error:  # pragma: no cover - depends on environment
        pytest.skip(f"Live RWA environment is not available: {error}")
    finally:
        db_client.close()


@pytest.fixture(scope="function")
def auth_credentials(created_user, generated_user_data) -> AuthCredentials:
    """Expose the dynamic user's login credentials after the fixture-created user has been provisioned."""
    return AuthCredentials(username=created_user.username, password=generated_user_data.password)


@pytest.fixture(scope="function")
def seeded_business_data_state(test_data_service) -> None:
    """Reset to the seeded baseline before the test and restore it again during teardown."""
    test_data_service.seed_database()
    try:
        yield
    finally:
        test_data_service.seed_database()


@pytest.fixture(scope="function")
def seeded_business_user_credentials(seeded_business_data_state, seeded_business_username) -> AuthCredentials:
    """Provide seeded-user credentials after the seeded baseline has been restored for the test."""
    return AuthCredentials(
        username=seeded_business_username,
        password=os.getenv("RWA_PASSWORD", "s3cret"),
    )


@pytest.fixture(scope="function")
def seeded_business_user(seeded_business_data_state, connected_users_repository, seeded_business_username):
    """Load the seeded business user record after the test reset fixture restores the baseline."""
    user_record = connected_users_repository.get_user_by_username(seeded_business_username)
    if user_record is None:  # pragma: no cover - defensive guard
        raise RuntimeError(f"Expected seeded business user {seeded_business_username} in lowdb data.")
    return user_record


@pytest.fixture(scope="function")
def seeded_send_money_contact(
    seeded_business_data_state,
    seeded_business_user,
    connected_contacts_repository,
    connected_users_repository,
):
    """Resolve one deterministic seeded contact so send-money slices use a stable receiver after reset."""
    contact_user_ids = connected_contacts_repository.get_contact_user_ids_for_user(seeded_business_user["id"])
    assert_that(contact_user_ids, "Expected seeded business user to have at least one contact").is_not_empty()

    contact_record = connected_users_repository.get_user_by_id(contact_user_ids[0])
    if contact_record is None:  # pragma: no cover - defensive guard
        raise RuntimeError(f"Expected seeded contact user {contact_user_ids[0]} to exist in lowdb data.")

    assert_that(
        connected_contacts_repository.has_contact_relationship(seeded_business_user["id"], contact_record["id"]),
        "Expected explicit seeded contact relationship for send-money slice",
    ).is_true()
    return contact_record


@pytest.fixture(scope="function")
def seeded_send_money_contact_credentials(
    seeded_business_data_state,
    seeded_send_money_contact,
) -> AuthCredentials:
    """Provide the seeded receiver credentials so side-effect checks can authenticate as the other participant."""
    return AuthCredentials(
        username=seeded_send_money_contact["username"],
        password=os.getenv("RWA_PASSWORD", "s3cret"),
    )
