from fastapi import status
from fastapi.testclient import TestClient
from app.core.security import decode_access_token

def test_register_user_successfully(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "nickname": "测试用户",
            "password": "strong-password",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["id"] == 1
    assert data["email"] == "user@example.com"
    assert data["nickname"] == "测试用户"
    assert "created_at" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_rejects_duplicate_email(
    client: TestClient,
) -> None:
    user_data = {
        "email": "user@example.com",
        "nickname": "测试用户",
        "password": "strong-password",
    }

    first_response = client.post(
        "/auth/register",
        json=user_data,
    )
    second_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert first_response.status_code == status.HTTP_201_CREATED
    assert second_response.status_code == status.HTTP_409_CONFLICT
    assert second_response.json() == {
        "detail": "该邮箱已经注册",
    }


def test_login_returns_access_token(
    client: TestClient,
) -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "nickname": "测试用户",
            "password": "strong-password",
        },
    )

    user_id = register_response.json()["id"]

    response = client.post(
        "/auth/login",
        data={
            "username": "user@example.com",
            "password": "strong-password",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["token_type"] == "bearer"
    assert "access_token" in data

    payload = decode_access_token(data["access_token"])

    assert payload["sub"] == str(user_id)


def test_login_rejects_wrong_password(
    client: TestClient,
) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "nickname": "测试用户",
            "password": "strong-password",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "user@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "邮箱或密码错误",
    }


def test_login_rejects_unknown_email(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "strong-password",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "邮箱或密码错误",
    }