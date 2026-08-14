from fastapi import status
from fastapi.testclient import TestClient

from tests.test_categories import register_and_get_token


def create_category(
    client: TestClient,
    token: str,
    name: str = "餐饮",
    category_type: str = "expense",
) -> dict[str, object]:
    response = client.post(
        "/categories",
        json={
            "name": name,
            "type": category_type,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


def test_create_transaction(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )
    category = create_category(client, token)

    response = client.post(
        "/transactions",
        json={
            "amount": "35.50",
            "type": "expense",
            "occurred_on": "2026-08-12",
            "note": "午餐",
            "category_id": category["id"],
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["amount"] == "35.50"
    assert data["type"] == "expense"
    assert data["occurred_on"] == "2026-08-12"
    assert data["note"] == "午餐"
    assert data["category_id"] == category["id"]
    assert data["user_id"] == category["user_id"]


def test_create_transaction_rejects_type_mismatch(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )
    category = create_category(client, token)

    response = client.post(
        "/transactions",
        json={
            "amount": "100.00",
            "type": "income",
            "occurred_on": "2026-08-12",
            "category_id": category["id"],
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": {
            "code": "TRANSACTION_TYPE_MISMATCH",
            "message": "流水类型必须和分类类型一致",
        },
    }


def test_create_transaction_rejects_other_users_category(
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
    category = create_category(client, first_token)

    response = client.post(
        "/transactions",
        json={
            "amount": "35.50",
            "type": "expense",
            "occurred_on": "2026-08-12",
            "category_id": category["id"],
        },
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"]["code"] == "CATEGORY_NOT_FOUND"


def test_create_transaction_requires_login(
    client: TestClient,
) -> None:
    response = client.post(
        "/transactions",
        json={
            "amount": "35.50",
            "type": "expense",
            "occurred_on": "2026-08-12",
            "category_id": 1,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_transactions_returns_only_current_user_transactions(
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

    first_category = create_category(
        client,
        first_token,
        name="餐饮",
    )
    second_category = create_category(
        client,
        second_token,
        name="交通",
    )

    older_response = client.post(
        "/transactions",
        json={
            "amount": "20.00",
            "type": "expense",
            "occurred_on": "2026-08-10",
            "note": "早餐",
            "category_id": first_category["id"],
        },
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )
    newer_response = client.post(
        "/transactions",
        json={
            "amount": "35.50",
            "type": "expense",
            "occurred_on": "2026-08-12",
            "note": "午餐",
            "category_id": first_category["id"],
        },
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    client.post(
        "/transactions",
        json={
            "amount": "10.00",
            "type": "expense",
            "occurred_on": "2026-08-13",
            "note": "公交",
            "category_id": second_category["id"],
        },
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    response = client.get(
        "/transactions",
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        newer_response.json(),
        older_response.json(),
    ]


def test_list_transactions_requires_login(
    client: TestClient,
) -> None:
    response = client.get("/transactions")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_transaction(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )
    category = create_category(client, token)
    headers = {
        "Authorization": f"Bearer {token}",
    }

    create_response = client.post(
        "/transactions",
        json={
            "amount": "35.50",
            "type": "expense",
            "occurred_on": "2026-08-12",
            "note": "午餐",
            "category_id": category["id"],
        },
        headers=headers,
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/transactions/{transaction_id}",
        json={
            "amount": "40.00",
            "note": "修改后的午餐",
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["amount"] == "40.00"
    assert response.json()["note"] == "修改后的午餐"
    assert response.json()["type"] == "expense"
    assert response.json()["category_id"] == category["id"]


def test_update_transaction_rejects_other_users_transaction(
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
    category = create_category(client, first_token)

    create_response = client.post(
        "/transactions",
        json={
            "amount": "35.50",
            "type": "expense",
            "occurred_on": "2026-08-12",
            "category_id": category["id"],
        },
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    response = client.patch(
        f"/transactions/{create_response.json()['id']}",
        json={
            "amount": "100.00",
        },
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"]["code"] == (
        "TRANSACTION_NOT_FOUND"
    )


def test_update_transaction_rejects_type_mismatch(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )
    category = create_category(client, token)
    headers = {
        "Authorization": f"Bearer {token}",
    }

    create_response = client.post(
        "/transactions",
        json={
            "amount": "35.50",
            "type": "expense",
            "occurred_on": "2026-08-12",
            "category_id": category["id"],
        },
        headers=headers,
    )

    response = client.patch(
        f"/transactions/{create_response.json()['id']}",
        json={
            "type": "income",
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"]["code"] == (
        "TRANSACTION_TYPE_MISMATCH"
    )


def test_delete_transaction(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )
    category = create_category(client, token)
    headers = {
        "Authorization": f"Bearer {token}",
    }

    create_response = client.post(
        "/transactions",
        json={
            "amount": "35.50",
            "type": "expense",
            "occurred_on": "2026-08-12",
            "category_id": category["id"],
        },
        headers=headers,
    )

    transaction_id = create_response.json()["id"]

    response = client.delete(
        f"/transactions/{transaction_id}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    list_response = client.get(
        "/transactions",
        headers=headers,
    )

    assert list_response.json() == []


def test_delete_transaction_rejects_other_users_transaction(
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
    category = create_category(client, first_token)

    create_response = client.post(
        "/transactions",
        json={
            "amount": "35.50",
            "type": "expense",
            "occurred_on": "2026-08-12",
            "category_id": category["id"],
        },
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    response = client.delete(
        f"/transactions/{create_response.json()['id']}",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": {
            "code": "TRANSACTION_NOT_FOUND",
            "message": "流水不存在",
        },
    }