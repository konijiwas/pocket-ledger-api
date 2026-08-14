from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionCreate(BaseModel):
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    type: TransactionType
    occurred_on: date
    note: str | None = Field(
        default=None,
        max_length=255,
    )
    category_id: int = Field(gt=0)


class TransactionUpdate(BaseModel):
    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    type: TransactionType | None = None
    occurred_on: date | None = None
    note: str | None = Field(
        default=None,
        max_length=255,
    )
    category_id: int | None = Field(
        default=None,
        gt=0,
    )


class TransactionRead(BaseModel):
    id: int
    amount: Decimal
    type: TransactionType
    occurred_on: date
    note: str | None
    category_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)