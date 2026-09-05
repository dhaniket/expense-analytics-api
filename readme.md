# Expense Analytics API

A FastAPI-based backend for an expense tracking and analytics application. The
project provides a layered architecture with API routing, business logic,
data access, and SQLite persistence.

## Technology stack

- Python 3.10 or newer (verified with Python 3.13.5)
- FastAPI
- Pydantic
- Uvicorn
- SQLite (via Python's built-in `sqlite3` module)
- Pytest and FastAPI TestClient

The repository uses a pinned `requirements.txt` so that local environments can
install the same dependency versions.

## Project structure

```text
expense-analytics-api/
|-- app/
|   |-- __init__.py
|   |-- main.py                     # FastAPI application entrypoint
|   |-- api/
|   |   |-- __init__.py
|   |   `-- expenses.py             # Expense router (CRUD + list endpoints)
|   |-- db/
|   |   |-- __init__.py
|   |   `-- database.py             # SQLite connection and table init
|   |-- models/
|   |   |-- __init__.py
|   |   `-- expense.py              # Domain model (frozen dataclass)
|   |-- repositories/
|   |   |-- __init__.py
|   |   `-- expense_repository.py   # SQLite data access layer
|   |-- schemas/
|   |   |-- __init__.py
|   |   `-- expense.py              # Pydantic request/response models
|   `-- services/
|       |-- __init__.py
|       `-- expense_service.py      # Business logic layer
|-- tests/
|   |-- __init__.py
|   |-- conftest.py                 # Shared fixtures (test client, temp DB)
|   `-- test_expenses.py            # Full test suite
|-- .gitignore
|-- expenses.db                     # SQLite database (auto-created, git-ignored)
|-- requirements.txt
`-- readme.md
```

### Architecture layers

Requests flow through four distinct layers:

```text
HTTP Request
    |
    v
[API Layer]          app/api/              Routes, request parsing, response formatting
    |
    v
[Service Layer]      app/services/         Business logic (validation, transformation)
    |
    v
[Repository Layer]   app/repositories/     Data access, SQL queries
    |
    v
[Database Layer]     app/db/               Connection management, schema DDL
    |
    v
[SQLite]             expenses.db           File-based database
```

Domain models (`app/models/`) and Pydantic schemas (`app/schemas/`) are shared
across layers but kept separate to isolate the API contract from domain logic.

## Getting started

### 1. Create a virtual environment

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If PowerShell blocks the activation script, either use Command Prompt with
`.venv\Scripts\activate.bat` or review your PowerShell execution policy.

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Start the API

Run this command from the repository root:

```bash
python -m uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API documentation

FastAPI generates interactive documentation while the server is running:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Available endpoints

### Health check

```http
GET /health
```

Example request:

```bash
curl http://127.0.0.1:8000/health
```

Successful response (`200 OK`):

```json
{
  "status": "ok"
}
```

### Create expense

```http
POST /expenses
Content-Type: application/json
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"amount": "249.99", "category": "Groceries", "description": "Weekly grocery shopping", "expense_date": "2026-09-06"}'
```

Successful response (`201 Created`):

```json
{
  "id": 1,
  "amount": "249.99",
  "category": "Groceries",
  "description": "Weekly grocery shopping",
  "expense_date": "2026-09-06"
}
```

### Get expense by ID

```http
GET /expenses/{expense_id}
```

Example request:

```bash
curl http://127.0.0.1:8000/expenses/1
```

Successful response (`200 OK`):

```json
{
  "id": 1,
  "amount": "249.99",
  "category": "Groceries",
  "description": "Weekly grocery shopping",
  "expense_date": "2026-09-06"
}
```

Returns `404 Not Found` if the expense does not exist.

### List expenses

```http
GET /expenses
GET /expenses?category=Food
GET /expenses?start_date=2026-09-01&end_date=2026-09-30
GET /expenses?category=Food&start_date=2026-09-01&end_date=2026-09-30
```

Supports optional query parameters for filtering:

| Parameter | Type | Description |
| --- | --- | --- |
| `category` | String | Filter by exact category match (1-50 chars) |
| `start_date` | Date | Filter expenses on or after this date |
| `end_date` | Date | Filter expenses on or before this date |

Example request:

```bash
curl "http://127.0.0.1:8000/expenses?category=Food&start_date=2026-09-01&end_date=2026-09-30"
```

Successful response (`200 OK`):

```json
[
  {
    "id": 1,
    "amount": "249.99",
    "category": "Food",
    "description": "Weekly grocery shopping",
    "expense_date": "2026-09-06"
  }
]
```

Returns `400 Bad Request` if `start_date` is after `end_date`.

Expenses are sorted by date descending (most recent first).

### Delete expense

```http
DELETE /expenses/{expense_id}
```

Example request:

```bash
curl -X DELETE http://127.0.0.1:8000/expenses/1
```

Successful response (`204 No Content`): empty body.

Returns `404 Not Found` if the expense does not exist.

## Expense schemas

The models in `app/schemas/expense.py` define request and response validation
for expense endpoints.

### `ExpenseCreate`

| Field | Type | Validation |
| --- | --- | --- |
| `amount` | Decimal | Must be greater than `0`, max 12 digits, 2 decimal places |
| `category` | String | Between 1 and 50 characters |
| `description` | String | Between 1 and 255 characters |
| `expense_date` | Date | ISO 8601 date, such as `2026-09-06` |

Text fields are stripped of leading/trailing whitespace and rejected if empty.

### `ExpenseResponse`

The response schema contains all `ExpenseCreate` fields plus an integer `id`.
Using `Decimal` for monetary values avoids the rounding behavior associated with
binary floating-point numbers.

### Domain model

The `Expense` dataclass in `app/models/expense.py` is a frozen (immutable)
domain object used internally. Amounts are stored in the database as integers
(paise/cents) and converted to `Decimal` at the repository boundary.

## Running tests

From the repository root, with the virtual environment activated:

```bash
python -m pytest
```

For compact output:

```bash
python -m pytest -q
```

### Test coverage

The test suite covers all endpoints and edge cases:

| Test | Description |
| --- | --- |
| `test_health_check` | Health endpoint returns `200` with `{"status": "ok"}` |
| `test_create_expense` | Creating an expense returns `201` with correct data |
| `test_create_expense_rejects_negative_amount` | Negative amounts are rejected with `422` |
| `test_create_expense_rejects_blank_category` | Whitespace-only categories are rejected with `422` |
| `test_get_expense` | Fetching an existing expense returns `200` |
| `test_get_missing_expense_returns_404` | Fetching a nonexistent ID returns `404` |
| `test_list_expenses` | Listing all expenses returns all records |
| `test_filter_expenses_by_category` | Category filtering returns only matching expenses |
| `test_filter_expenses_by_date_range` | Date range filtering returns only expenses within range |
| `test_invalid_date_range_returns_400` | `start_date > end_date` returns `400` |
| `test_delete_expense` | Deleting returns `204`, subsequent GET returns `404` |
| `test_delete_missing_expense_returns_404` | Deleting a nonexistent ID returns `404` |

Tests use an isolated temporary database per test via `conftest.py` fixtures to
avoid any side effects between tests.

## Configuration and persistence

The application uses SQLite with the database file `expenses.db` at the project
root. The table is created automatically on startup via `initialize_database()`.
`.env` files and `*.db` files are ignored by Git.

No environment variables are required. The database path is resolved relative to
the project root in `app/db/database.py`.

## License

No license file is currently included. Add one before distributing or accepting
external contributions to clarify permitted use.
