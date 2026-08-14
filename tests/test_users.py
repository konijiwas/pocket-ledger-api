from fastapi import status
from fastapi.testclient import TestClient


def test_read_current_user(
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

    login_response = client.post(
        "/auth/login",
        data={
            "username": "user@example.com",
            "password": "strong-password",
        },
    )

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": register_response.json()["id"],
        "email": "user@example.com",
        "nickname": "测试用户",
        "created_at": register_response.json()["created_at"],
    }


def test_read_current_user_requires_token(
    client: TestClient,
) -> None:
    response = client.get("/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated",
    }


def test_read_current_user_rejects_invalid_token(
    client: TestClient,
) -> None:
    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "无法验证登录身份",
    }