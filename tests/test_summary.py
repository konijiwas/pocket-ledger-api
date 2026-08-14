from fastapi import status
from fastapi.testclient import TestClient

from tests.test_categories import register_and_get_token
from tests.test_transactions import create_category


def test_read_summary_calculates_totals(
    client: TestClient,
) -> None:
    token = register_and_get_token(
        client,
        email="user@example.com",
        nickname="测试用户",
    )
    income_category = create_category(
        client,
        token,
        name="工资",
        category_type="income",
    )
    expense_category = create_category(
        client,
        token,
        name="餐饮",
        category_type="expense",
    )
    headers = {
        "Authorization": f"Bearer {token}",
    }

    client.post(
        "/transactions",
        json={
            "amount": "5000.00",
            "type": "income",
            "occurred_on": "2026-08-01",
            "category_id": income_category["id"],
        },
        headers=headers,
    )
    client.post(
        "/transactions",
        json={
            "amount": "1250.50",
            "type": "expense",
            "occurred_on": "2026-08-02",
            "category_id": expense_category["id"],
        },
        headers=headers,
    )

    response = client.get(
        "/summary",
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "income_total": "5000.00",
        "expense_total": "1250.50",
        "balance": "3749.50",
    }


def test_read_summary_returns_only_current_user_totals(
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
        name="工资",
        category_type="income",
    )
    second_category = create_category(
        client,
        second_token,
        name="工资",
        category_type="income",
    )

    client.post(
        "/transactions",
        json={
            "amount": "100.00",
            "type": "income",
            "occurred_on": "2026-08-01",
            "category_id": first_category["id"],
        },
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )
    client.post(
        "/transactions",
        json={
            "amount": "900.00",
            "type": "income",
            "occurred_on": "2026-08-01",
            "category_id": second_category["id"],
        },
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    response = client.get(
        "/summary",
        headers={
            "Authorization": f"Bearer {first_token}",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "income_total": "100.00",
        "expense_total": "0.00",
        "balance": "100.00",
    }


def test_read_summary_requires_login(
    client: TestClient,
) -> None:
    response = client.get("/summary")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED