from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.db
class TestTransactionDetailRepository:
    """DB coverage for persisted transaction-detail data."""

    def test_transaction_detail_repository_returns_the_created_payment(
        self,
        require_live_rwa_environment,
        connected_transactions_repository,
        seeded_sent_payment,
    ):
        """Create a seeded payment through fixtures and verify the persisted lowdb transaction matches it."""
        persisted_transaction = connected_transactions_repository.get_transaction_by_id(seeded_sent_payment.id)

        attach_json(
            name="transaction-detail-db",
            content={
                "source_transaction": seeded_sent_payment.__dict__,
                "db_transaction_detail": persisted_transaction.__dict__ if persisted_transaction else None,
            },
        )

        assert_that(
            persisted_transaction,
            "Transaction detail repository should return the created payment by id",
        ).is_not_none()

        with soft_assertions():
            assert_that(persisted_transaction.id, "Persisted transaction id should match").is_equal_to(
                seeded_sent_payment.id
            )
            assert_that(persisted_transaction.description, "Persisted transaction description should match").is_equal_to(
                seeded_sent_payment.description
            )
            assert_that(persisted_transaction.amount, "Persisted transaction amount should match").is_equal_to(
                seeded_sent_payment.amount
            )
            assert_that(persisted_transaction.sender_id, "Persisted sender id should match").is_equal_to(
                seeded_sent_payment.sender_id
            )
            assert_that(persisted_transaction.receiver_id, "Persisted receiver id should match").is_equal_to(
                seeded_sent_payment.receiver_id
            )
            assert_that(persisted_transaction.sender_name, "Persisted sender name should match").is_equal_to(
                seeded_sent_payment.sender_name
            )
            assert_that(persisted_transaction.receiver_name, "Persisted receiver name should match").is_equal_to(
                seeded_sent_payment.receiver_name
            )
            assert_that(persisted_transaction.status, "Persisted transaction status should be complete").is_equal_to(
                "complete"
            )
