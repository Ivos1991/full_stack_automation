from __future__ import annotations

import pytest


@pytest.fixture(scope="function")
def ui_created_transaction_comment_setup(
    sign_in_page,
    home_page,
    transaction_create_page,
    transaction_detail_page,
    connected_comments_repository,
    connected_transactions_repository,
    seeded_business_user,
    seeded_business_user_credentials,
    seeded_send_money_contact,
    seeded_send_money_payment,
    seeded_transaction_comment_payload,
):
    """Create a seeded payment and comment through the UI so related E2E tests can reuse one visible setup path."""
    recipient_full_name = (
        f"{seeded_send_money_contact['firstName']} {seeded_send_money_contact['lastName']}"
    )

    sign_in_page.go_to()
    sign_in_page.sign_in(
        username=seeded_business_user_credentials.username,
        password=seeded_business_user_credentials.password,
    )
    home_page.expect_seeded_user_landing_loaded()
    home_page.open_new_transaction()

    transaction_create_page.search_contact(seeded_send_money_contact["firstName"])
    transaction_create_page.select_contact_by_full_name(recipient_full_name)
    transaction_create_page.expect_payment_form_loaded(recipient_full_name=recipient_full_name)
    transaction_create_page.enter_amount(seeded_send_money_payment.amount)
    transaction_create_page.enter_description(seeded_send_money_payment.description)
    transaction_create_page.submit_payment()
    transaction_create_page.expect_payment_success_state(
        amount_display=seeded_send_money_payment.amount_display,
        description=seeded_send_money_payment.description,
    )
    transaction_create_page.return_to_transactions()

    home_page.open_personal_feed()
    home_page.open_transaction_with_description(seeded_send_money_payment.description)

    persisted_transaction = connected_transactions_repository.get_latest_payment_by_participants_and_description(
        sender_id=seeded_business_user["id"],
        receiver_id=seeded_send_money_contact["id"],
        description=seeded_send_money_payment.description,
    )
    if persisted_transaction is None:  # pragma: no cover - defensive guard
        raise RuntimeError("Expected UI-created seeded payment before shared transaction-comment assertions.")

    transaction_detail_page.expect_loaded()
    transaction_detail_page.add_comment(
        transaction_id=persisted_transaction.id,
        content=seeded_transaction_comment_payload.content,
    )
    transaction_detail_page.expect_comment_displayed(seeded_transaction_comment_payload.content)

    db_comment = connected_comments_repository.get_comment_by_transaction_and_content(
        transaction_id=persisted_transaction.id,
        content=seeded_transaction_comment_payload.content,
    )
    if db_comment is None:  # pragma: no cover - defensive guard
        raise RuntimeError("Expected persisted transaction comment before shared notification assertions.")

    return {
        "transaction": persisted_transaction,
        "comment": db_comment,
        "detail_page": transaction_detail_page,
    }


@pytest.fixture(scope="function")
def ui_created_transaction_comment_transaction(ui_created_transaction_comment_setup):
    """Expose the UI-created persisted transaction for E2E assertions."""
    return ui_created_transaction_comment_setup["transaction"]


@pytest.fixture(scope="function")
def ui_created_transaction_comment_record(ui_created_transaction_comment_setup):
    """Expose the persisted UI-created comment for E2E assertions."""
    return ui_created_transaction_comment_setup["comment"]


@pytest.fixture(scope="function")
def ui_created_transaction_comment_detail_page(ui_created_transaction_comment_setup):
    """Expose the transaction detail page left open by the shared E2E setup."""
    return ui_created_transaction_comment_setup["detail_page"]
