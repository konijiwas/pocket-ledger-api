import pytest
from pydantic import ValidationError

from app.schemas.transaction import (
    TransactionCreate,
    TransactionType,
    TransactionUpdate,
)


def test_transaction_create_accepts_valid_data() -> None:
    transaction = TransactionCreate(
        amount="12.50",
        type="expense",
        occurred_on="2026-08-12",
        note="午餐",
        category_id=1,
    )

    assert str(transaction.amount) == "12.50"
    assert transaction.type == TransactionType.EXPENSE
    assert transaction.category_id == 1


def test_transaction_create_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationError):
        TransactionCreate(
            amount="0",
            type="expense",
            occurred_on="2026-08-12",
            category_id=1,
        )


def test_transaction_create_rejects_too_many_decimal_places() -> None:
    with pytest.raises(ValidationError):
        TransactionCreate(
            amount="12.345",
            type="expense",
            occurred_on="2026-08-12",
            category_id=1,
        )


def test_transaction_create_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        TransactionCreate(
            amount="12.50",
            type="transfer",
            occurred_on="2026-08-12",
            category_id=1,
        )


def test_transaction_update_accepts_partial_data() -> None:
    transaction = TransactionUpdate(
        note="修改后的备注",
    )

    assert transaction.amount is None
    assert transaction.note == "修改后的备注"