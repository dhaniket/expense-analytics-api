from datetime import date
from decimal import Decimal

from app.api.dependencies import (
    get_expense_service,
)
from app.main import app
from app.models.expense import Expense


class StubExpenseService:

    def get_expense(
        self,
        expense_id: int,
    ) -> Expense:

        return Expense(
            id=expense_id,
            amount=Decimal("99.99").quantize(Decimal("0.01")),
            category="Test",
            description="Injected expense",
            expense_date=date(
                2026,
                9,
                8,
            ),
        )


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_expense(client):
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "450.50",
            "category": "Food",
            "description": "Dinner",
            "expense_date": "2026-09-06",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["amount"] == "450.50"
    assert data["category"] == "Food"
    assert data["description"] == "Dinner"
    assert data["expense_date"] == "2026-09-06"


def test_create_expense_rejects_negative_amount(
    client,
):
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "-100",
            "category": "Food",
            "description": "Dinner",
            "expense_date": "2026-09-06",
        },
    )

    assert response.status_code == 422


def test_create_expense_rejects_blank_category(
    client,
):
    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "100",
            "category": "   ",
            "description": "Dinner",
            "expense_date": "2026-09-06",
        },
    )

    assert response.status_code == 422


def test_get_expense(client):
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.00",
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-06",
        },
    )

    expense_id = create_response.json()["id"]

    response = client.get(f"/api/v1/expenses/{expense_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == expense_id
    assert data["amount"] == "250.00"
    assert data["category"] == "Food"
    assert data["description"] == "Lunch"
    assert data["expense_date"] == "2026-09-06"


def test_get_missing_expense_returns_404(
    client,
):
    expense_id = 99999
    response = client.get(f"/api/v1/expenses/{expense_id}")

    assert response.status_code == 404

    assert response.json() == {
        "error": {
            "code": "EXPENSE_NOT_FOUND",
            "message": (f"Expense {expense_id} not found"),
        }
    }


def test_list_expenses(client):
    client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.00",
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-05",
        },
    )

    client.post(
        "/api/v1/expenses",
        json={
            "amount": "800.00",
            "category": "Travel",
            "description": "Cab",
            "expense_date": "2026-09-06",
        },
    )

    response = client.get("/api/v1/expenses")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2


def test_filter_expenses_by_category(
    client,
):
    client.post(
        "/api/v1/expenses",
        json={
            "amount": "200.00",
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-05",
        },
    )

    client.post(
        "/api/v1/expenses",
        json={
            "amount": "1000.00",
            "category": "Travel",
            "description": "Train",
            "expense_date": "2026-09-06",
        },
    )

    response = client.get("/api/v1/expenses?category=Food")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["category"] == "Food"


def test_filter_expenses_by_date_range(
    client,
):
    client.post(
        "/api/v1/expenses",
        json={
            "amount": "100.00",
            "category": "Food",
            "description": "Breakfast",
            "expense_date": "2026-09-01",
        },
    )

    client.post(
        "/api/v1/expenses",
        json={
            "amount": "200.00",
            "category": "Food",
            "description": "Dinner",
            "expense_date": "2026-09-05",
        },
    )

    response = client.get(
        "/api/v1/expenses" "?start_date=2026-09-04" "&end_date=2026-09-06"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1

    assert data["items"][0]["expense_date"] == "2026-09-05"


def test_invalid_date_range_returns_400(
    client,
):
    response = client.get(
        "/api/v1/expenses" "?start_date=2026-09-10" "&end_date=2026-09-01"
    )

    assert response.status_code == 400

    assert response.json() == {
        "error": {
            "code": "INVALID_DATE_RANGE",
            "message": "start_date cannot be after end_date",
        }
    }


def test_delete_expense(client):
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "600.00",
            "category": "Shopping",
            "description": "Keyboard",
            "expense_date": "2026-09-06",
        },
    )

    expense_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/expenses/{expense_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/expenses/{expense_id}")

    assert get_response.status_code == 404


def test_delete_missing_expense_returns_404(
    client,
):
    response = client.delete("/api/v1/expenses/999999")

    assert response.status_code == 404


def test_expense_pagination(
    client,
):
    for index in range(5):

        client.post(
            "/api/v1/expenses",
            json={
                "amount": str(100 + index),
                "category": "Food",
                "description": f"Expense {index}",
                "expense_date": "2026-09-06",
            },
        )

    response = client.get("/api/v1/expenses" "?limit=2" "&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2

    assert data["limit"] == 2

    assert data["offset"] == 0


def test_expense_limit_cannot_exceed_100(
    client,
):
    response = client.get("/api/v1/expenses" "?limit=101")

    assert response.status_code == 422


def test_service_dependency_can_be_overridden(
    client,
):

    stub_service = StubExpenseService()

    app.dependency_overrides[get_expense_service] = lambda: stub_service

    try:

        response = client.get("/api/v1/expenses/123")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 123

        assert data["amount"] == "99.99"

        assert data["category"] == "Test"

    finally:

        app.dependency_overrides.pop(
            get_expense_service,
            None,
        )


def test_update_expense(
    client,
):
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "250.00",
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-08",
        },
    )

    expense_id = create_response.json()["id"]

    response = client.patch(
        (f"/api/v1/expenses/" f"{expense_id}"),
        json={"amount": "300.00"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == "300.00"

    assert data["category"] == "Food"

    assert data["description"] == "Lunch"

    assert data["expense_date"] == "2026-09-08"

    get_response = client.get(f"/api/v1/expenses/{expense_id}")

    assert get_response.status_code == 200

    saved = get_response.json()

    assert saved["amount"] == "300.00"

    assert saved["category"] == "Food"


def test_update_expense_rejects_null_description(
    client,
):
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "500.00",
            "category": "Food",
            "description": "Dinner",
            "expense_date": "2026-09-08",
        },
    )

    assert create_response.status_code == 201

    expense_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/expenses/{expense_id}",
        json={"description": None},
    )

    assert response.status_code == 422


def test_update_expense_rejects_negative_amount(
    client,
):
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "500.00",
            "category": "Food",
            "description": "Test expense",
            "expense_date": "2026-09-08",
        },
    )

    expense_id = create_response.json()["id"]

    response = client.patch(
        (f"/api/v1/expenses/" f"{expense_id}"),
        json={"amount": "-1"},
    )

    assert response.status_code == 422


def test_update_expense_rejects_empty_body(
    client,
):
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "500.00",
            "category": "Food",
            "description": "Test expense",
            "expense_date": "2026-09-08",
        },
    )

    expense_id = create_response.json()["id"]

    response = client.patch(
        (f"/api/v1/expenses/" f"{expense_id}"),
        json={},
    )

    assert response.status_code == 422


def test_update_missing_expense_returns_404(
    client,
):
    response = client.patch(
        "/api/v1/expenses/99999",
        json={"amount": "500.00"},
    )

    assert response.status_code == 404

    assert response.json() == {
        "error": {
            "code": "EXPENSE_NOT_FOUND",
            "message": "Expense 99999 not found",
        }
    }


def test_update_expense_rejects_null_amount(
    client,
):
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "500.00",
            "category": "Food",
            "description": "Test expense",
            "expense_date": "2026-09-08",
        },
    )

    expense_id = create_response.json()["id"]

    response = client.patch(
        (f"/api/v1/expenses/" f"{expense_id}"),
        json={"amount": None},
    )

    assert response.status_code == 422
