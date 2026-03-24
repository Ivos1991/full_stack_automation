from __future__ import annotations
import os
import pytest
from src.api.schemas.user_models import GeneratedUserData
from src.testdata.factories.user_factory import UserFactory
from src.api.schemas.comment_models import CommentCreatePayload
from src.api.schemas.transaction_models import TransactionCreatePayload
from src.testdata.builders.payload_builders import (
    build_health_payload,
    build_seeded_send_money_payment_payload,
    build_seeded_transaction_comment_payload,
)

@pytest.fixture(scope="function")
def user_factory() -> UserFactory:
    return UserFactory()


@pytest.fixture(scope="function")
def health_payload() -> dict[str, str]:
    return build_health_payload()


@pytest.fixture(scope="function")
def generated_user_data(user_factory: UserFactory) -> GeneratedUserData:
    return user_factory.build_rwa_user()


@pytest.fixture(scope="function")
def seeded_business_username() -> str:
    return os.getenv("RWA_USERNAME", "Heath93")


@pytest.fixture(scope="function")
def seeded_send_money_payment(seeded_send_money_contact) -> TransactionCreatePayload:
    return build_seeded_send_money_payment_payload(receiver_id=seeded_send_money_contact["id"])


@pytest.fixture(scope="function")
def seeded_transaction_comment_payload() -> CommentCreatePayload:
    return build_seeded_transaction_comment_payload()
