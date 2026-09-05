def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_expense(client):
    response = client.post(
        "/expenses",
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
        "/expenses",
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
        "/expenses",
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
        "/expenses",
        json={
            "amount": "250.00",
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-06",
        },
    )

    expense_id = create_response.json()["id"]

    response = client.get(f"/expenses/{expense_id}")

    assert response.status_code == 200

    assert response.json()["category"] == "Food"


def test_get_missing_expense_returns_404(
    client,
):
    response = client.get("/expenses/99999")

    assert response.status_code == 404

    assert response.json() == {"detail": "Expense not found"}


def test_list_expenses(client):
    client.post(
        "/expenses",
        json={
            "amount": "250.00",
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-05",
        },
    )

    client.post(
        "/expenses",
        json={
            "amount": "800.00",
            "category": "Travel",
            "description": "Cab",
            "expense_date": "2026-09-06",
        },
    )

    response = client.get("/expenses")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_filter_expenses_by_category(
    client,
):
    client.post(
        "/expenses",
        json={
            "amount": "200.00",
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-05",
        },
    )

    client.post(
        "/expenses",
        json={
            "amount": "1000.00",
            "category": "Travel",
            "description": "Train",
            "expense_date": "2026-09-06",
        },
    )

    response = client.get("/expenses?category=Food")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Food"


def test_filter_expenses_by_date_range(
    client,
):
    client.post(
        "/expenses",
        json={
            "amount": "100.00",
            "category": "Food",
            "description": "Breakfast",
            "expense_date": "2026-09-01",
        },
    )

    client.post(
        "/expenses",
        json={
            "amount": "200.00",
            "category": "Food",
            "description": "Dinner",
            "expense_date": "2026-09-05",
        },
    )

    response = client.get("/expenses" "?start_date=2026-09-04" "&end_date=2026-09-06")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["expense_date"] == "2026-09-05"


def test_invalid_date_range_returns_400(
    client,
):
    response = client.get("/expenses" "?start_date=2026-09-10" "&end_date=2026-09-01")

    assert response.status_code == 400

    assert response.json() == {"detail": "start_date cannot be after end_date"}


def test_delete_expense(client):
    create_response = client.post(
        "/expenses",
        json={
            "amount": "600.00",
            "category": "Shopping",
            "description": "Keyboard",
            "expense_date": "2026-09-06",
        },
    )

    expense_id = create_response.json()["id"]

    delete_response = client.delete(f"/expenses/{expense_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/expenses/{expense_id}")

    assert get_response.status_code == 404


def test_delete_missing_expense_returns_404(
    client,
):
    response = client.delete("/expenses/999999")

    assert response.status_code == 404
