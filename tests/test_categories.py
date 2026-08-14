from fastapi import status
from fastapi.testclient import TestClient


def register_and_get_token(
    client: TestClient,
    email: str,
    nickname: str,
) -> str:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "nickname": nickname,
            "password": "strong-password",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "strong-password",
        },
    )

    return login_response.json()["access_token"]


def test_create_category(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )

    response = client.post(
        "/categories",
        json={
            "name": "工资",
            "type": "income",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "工资"
    assert data["type"] == "income"
    assert data["user_id"] == 1
    assert "created_at" in data


def test_create_category_requires_login(
    client: TestClient,
) -> None:
    response = client.post(
        "/categories",
        json={
            "name": "工资",
            "type": "income",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_category_rejects_duplicate(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )

    request_data = {
        "name": "工资",
        "type": "income",
    }
    headers = {
        "Authorization": f"Bearer {token}",
    }

    first_response = client.post(
        "/categories",
        json=request_data,
        headers=headers,
    )
    second_response = client.post(
        "/categories",
        json=request_data,
        headers=headers,
    )

    assert first_response.status_code == status.HTTP_201_CREATED
    assert second_response.status_code == status.HTTP_409_CONFLICT
    assert second_response.json() == {
        "detail": {
            "code": "CATEGORY_ALREADY_EXISTS",
            "message": "该分类已经存在",
        },
    }


def test_different_users_can_use_same_category(
    client: TestClient,
) -> None:
    first_token = register_and_get_token(
        client,
        email="first@example.com",
        nickname="用户一",
    )
    second_token = register_and_get_token(
        client,
        email="second@example.com",
        nickname="用户二",
    )

    request_data = {
        "name": "工资",
        "type": "income",
    }

    first_response = client.post(
        "/categories",
        json=request_data,
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )
    second_response = client.post(
        "/categories",
        json=request_data,
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert first_response.status_code == status.HTTP_201_CREATED
    assert second_response.status_code == status.HTTP_201_CREATED
    assert (
        first_response.json()["user_id"]
        != second_response.json()["user_id"]
    )


def test_list_categories_returns_only_current_user_categories(
    client: TestClient,
) -> None:
    first_token = register_and_get_token(
        client,
        email="first@example.com",
        nickname="用户一",
    )
    second_token = register_and_get_token(
        client,
        email="second@example.com",
        nickname="用户二",
    )

    first_response = client.post(
        "/categories",
        json={
            "name": "工资",
            "type": "income",
        },
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )
    second_response = client.post(
        "/categories",
        json={
            "name": "餐饮",
            "type": "expense",
        },
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert first_response.status_code == status.HTTP_201_CREATED
    assert second_response.status_code == status.HTTP_201_CREATED

    response = client.get(
        "/categories",
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        first_response.json(),
    ]


def test_list_categories_requires_login(
    client: TestClient,
) -> None:
    response = client.get("/categories")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_category(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )
    headers = {
        "Authorization": f"Bearer {token}",
    }

    create_response = client.post(
        "/categories",
        json={
            "name": "工资",
            "type": "income",
        },
        headers=headers,
    )

    category_id = create_response.json()["id"]

    response = client.patch(
        f"/categories/{category_id}",
        json={
            "name": "每月工资",
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "每月工资"
    assert response.json()["type"] == "income"


def test_update_category_rejects_other_users_category(
    client: TestClient,
) -> None:
    first_token = register_and_get_token(
        client,
        email="first@example.com",
        nickname="用户一",
    )
    second_token = register_and_get_token(
        client,
        email="second@example.com",
        nickname="用户二",
    )

    create_response = client.post(
        "/categories",
        json={
            "name": "工资",
            "type": "income",
        },
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    category_id = create_response.json()["id"]

    response = client.patch(
        f"/categories/{category_id}",
        json={
            "name": "非法修改",
        },
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": {
            "code": "CATEGORY_NOT_FOUND",
            "message": "分类不存在",
        },
    }


def test_update_category_rejects_duplicate(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )
    headers = {
        "Authorization": f"Bearer {token}",
    }

    first_response = client.post(
        "/categories",
        json={
            "name": "工资",
            "type": "income",
        },
        headers=headers,
    )
    client.post(
        "/categories",
        json={
            "name": "奖金",
            "type": "income",
        },
        headers=headers,
    )

    response = client.patch(
        f"/categories/{first_response.json()['id']}",
        json={
            "name": "奖金",
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"]["code"] == (
        "CATEGORY_ALREADY_EXISTS"
    )


def test_delete_category(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )
    headers = {
        "Authorization": f"Bearer {token}",
    }

    create_response = client.post(
        "/categories",
        json={
            "name": "工资",
            "type": "income",
        },
        headers=headers,
    )

    category_id = create_response.json()["id"]

    response = client.delete(
        f"/categories/{category_id}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    list_response = client.get(
        "/categories",
        headers=headers,
    )

    assert list_response.json() == []


def test_delete_category_rejects_other_users_category(
    client: TestClient,
) -> None:
    first_token = register_and_get_token(
        client,
        email="first@example.com",
        nickname="用户一",
    )
    second_token = register_and_get_token(
        client,
        email="second@example.com",
        nickname="用户二",
    )

    create_response = client.post(
        "/categories",
        json={
            "name": "工资",
            "type": "income",
        },
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    category_id = create_response.json()["id"]

    response = client.delete(
        f"/categories/{category_id}",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": {
            "code": "CATEGORY_NOT_FOUND",
            "message": "分类不存在",
        },
    }