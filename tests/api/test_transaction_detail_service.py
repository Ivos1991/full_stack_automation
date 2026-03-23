from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.api
class TestTransactionDetailService:
    def test_transaction_detail_api_returns_the_created_payment(
        self,
        require_live_rwa_environment,
        transactions_service,
        seeded_sent_payment,
    ):
        transaction_detail = transactions_service.get_transaction_by_id(seeded_sent_payment.id)

        attach_json(
            name="transaction-detail-api",
            content={
                "source_transaction": seeded_sent_payment.__dict__,
                "api_transaction_detail": transaction_detail.__dict__,
            },
        )

        with soft_assertions():
            assert_that(transaction_detail.id, "Transaction detail id should match the created payment").is_equal_to(
                seeded_sent_payment.id
            )
            assert_that(
                transaction_detail.description,
                "Transaction detail description should match the created payment",
            ).is_equal_to(seeded_sent_payment.description)
            assert_that(transaction_detail.amount, "Transaction detail amount should match").is_equal_to(
                seeded_sent_payment.amount
            )
            assert_that(transaction_detail.sender_id, "Transaction detail sender id should match").is_equal_to(
                seeded_sent_payment.sender_id
            )
            assert_that(transaction_detail.receiver_id, "Transaction detail receiver id should match").is_equal_to(
                seeded_sent_payment.receiver_id
            )
            assert_that(
                transaction_detail.sender_name,
                "Transaction detail sender name should match the created payment",
            ).is_equal_to(seeded_sent_payment.sender_name)
            assert_that(
                transaction_detail.receiver_name,
                "Transaction detail receiver name should match the created payment",
            ).is_equal_to(seeded_sent_payment.receiver_name)
            assert_that(transaction_detail.status, "Transaction detail status should remain complete").is_equal_to(
                "complete"
            )
