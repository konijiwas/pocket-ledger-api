import pytest
from pydantic import ValidationError

from app.schemas.category import (
    CategoryCreate,
    CategoryType,
    CategoryUpdate,
)


def test_category_create_accepts_valid_data() -> None:
    category = CategoryCreate(
        name="工资",
        type="income",
    )

    assert category.name == "工资"
    assert category.type == CategoryType.INCOME


def test_category_create_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        CategoryCreate(
            name="工资",
            type="other",
        )


def test_category_create_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        CategoryCreate(
            name="",
            type="income",
        )


def test_category_update_accepts_partial_data() -> None:
    category = CategoryUpdate(
        name="每月工资",
    )

    assert category.name == "每月工资"
    assert category.type is None