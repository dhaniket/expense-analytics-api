from datetime import date
from decimal import Decimal

import pytest

from app.errors.expense_errors import (
    ExpenseNotFoundError,
    InvalidExpenseDateRangeError,
)
from app.models.expense import Expense
from app.schemas.expense import ExpenseUpdate
from app.services.expense_service import (
    ExpenseService,
)


class FakeExpenseRepository:

    def __init__(
        self,
        expenses: list[Expense] | None = None,
    ) -> None:

        self.expenses = {expense.id: expense for expense in (expenses or [])}

    def get_by_id(
        self,
        expense_id: int,
    ) -> Expense | None:

        return self.expenses.get(expense_id)

    def update(
        self,
        expense: Expense,
    ) -> Expense | None:

        if expense.id not in self.expenses:
            return None

        self.expenses[expense.id] = expense

        return expense

    def delete(
        self,
        expense_id: int,
    ) -> bool:

        if expense_id not in self.expenses:
            return False

        del self.expenses[expense_id]

        return True

    def list(
        self,
        **kwargs,
    ) -> list[Expense]:

        return list(self.expenses.values())


def test_service_get_missing_expense():

    repository = FakeExpenseRepository()

    service = ExpenseService(repository)

    with pytest.raises(ExpenseNotFoundError):
        service.get_expense(999)


def test_service_rejects_invalid_date_range():

    repository = FakeExpenseRepository()

    service = ExpenseService(repository)

    with pytest.raises(InvalidExpenseDateRangeError):
        service.list_expenses(
            start_date=date(
                2026,
                9,
                10,
            ),
            end_date=date(
                2026,
                9,
                1,
            ),
        )


def test_service_partial_update_preserves_fields():

    existing = Expense(
        id=1,
        amount=Decimal("250.00"),
        category="Food",
        description="Lunch",
        expense_date=date(
            2026,
            9,
            8,
        ),
    )

    repository = FakeExpenseRepository([existing])

    service = ExpenseService(repository)

    update_data = ExpenseUpdate(amount=Decimal("300.00"))

    updated = service.update_expense(
        expense_id=1,
        update_data=update_data,
    )

    assert updated.amount == Decimal("300.00")

    assert updated.category == "Food"

    assert updated.description == "Lunch"

    assert updated.expense_date == date(
        2026,
        9,
        8,
    )


def test_service_partial_update_preserves_fields():

    existing = Expense(
        id=1,
        amount=Decimal("250.00"),
        category="Food",
        description="Lunch",
        expense_date=date(
            2026,
            9,
            8,
        ),
    )

    repository = FakeExpenseRepository([existing])

    service = ExpenseService(repository)

    update_data = ExpenseUpdate(amount=Decimal("300.00"))

    updated = service.update_expense(
        expense_id=1,
        update_data=update_data,
    )

    assert updated.amount == Decimal("300.00")

    assert updated.category == "Food"

    assert updated.description == "Lunch"

    assert updated.expense_date == date(
        2026,
        9,
        8,
    )


def test_service_delete_missing_expense():

    repository = FakeExpenseRepository()

    service = ExpenseService(repository)

    with pytest.raises(ExpenseNotFoundError):
        service.delete_expense(999)


def test_expense_id_must_be_positive(
    client,
):

    response = client.get("/api/v1/expenses/0")

    assert response.status_code == 422


def test_expense_id_rejects_negative_value(
    client,
):

    response = client.get("/api/v1/expenses/-1")

    assert response.status_code == 422


def test_invalid_sort_order_returns_422(
    client,
):

    response = client.get("/api/v1/expenses" "?sort_order=sideways")

    assert response.status_code == 422


def test_invalid_sort_field_returns_422(
    client,
):

    response = client.get("/api/v1/expenses" "?sort_by=password")

    assert response.status_code == 422


def test_unknown_query_parameter_returns_422(
    client,
):

    response = client.get("/api/v1/expenses" "?limmit=10")

    assert response.status_code == 422


def test_update_rejects_unknown_field(
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

    assert create_response.status_code == 201

    expense_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/expenses/{expense_id}",
        json={"random_field": "something"},
    )

    assert response.status_code == 422


def test_delete_returns_no_content(
    client,
):

    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "500.00",
            "category": "Food",
            "description": "Delete test",
            "expense_date": "2026-09-08",
        },
    )

    assert create_response.status_code == 201

    expense_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/expenses/{expense_id}")

    assert response.status_code == 204

    assert response.content == b""


def test_expense_pagination_offset(
    client,
):

    for index in range(5):

        response = client.post(
            "/api/v1/expenses",
            json={
                "amount": str(100 + index),
                "category": "Food",
                "description": f"Expense {index}",
                "expense_date": "2026-09-08",
            },
        )

        assert response.status_code == 201

    first_response = client.get(
        "/api/v1/expenses" "?limit=2" "&offset=0" "&sort_by=id" "&sort_order=asc"
    )

    second_response = client.get(
        "/api/v1/expenses" "?limit=2" "&offset=2" "&sort_by=id" "&sort_order=asc"
    )

    first_items = first_response.json()["items"]

    second_items = second_response.json()["items"]

    assert len(first_items) == 2
    assert len(second_items) == 2

    assert first_items[0]["description"] == "Expense 0"

    assert first_items[1]["description"] == "Expense 1"

    assert second_items[0]["description"] == "Expense 2"

    assert second_items[1]["description"] == "Expense 3"


def test_expense_amount_keeps_two_decimal_places(
    client,
):

    create_response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "300.00",
            "category": "Food",
            "description": "Money formatting",
            "expense_date": "2026-09-08",
        },
    )

    expense_id = create_response.json()["id"]

    response = client.get(f"/api/v1/expenses/{expense_id}")

    assert response.json()["amount"] == "300.00"


def test_openapi_contains_expense_routes(
    client,
):

    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/api/v1/expenses" in paths

    assert "/api/v1/expenses/{expense_id}" in paths

    assert "patch" in paths["/api/v1/expenses/{expense_id}"]
