import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate


def test_user_create_accepts_valid_data() -> None:
    user = UserCreate(
        email="user@example.com",
        nickname="测试用户",
        password="strong-password",
    )

    assert user.email == "user@example.com"
    assert user.nickname == "测试用户"


def test_user_create_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            nickname="测试用户",
            password="strong-password",
        )


def test_user_create_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            email="user@example.com",
            nickname="测试用户",
            password="1234567",
        )