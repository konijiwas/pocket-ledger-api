from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class CategoryType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=50,
    )
    type: CategoryType


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    type: CategoryType | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    type: CategoryType
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)