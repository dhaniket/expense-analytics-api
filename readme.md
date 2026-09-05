# Expense Analytics API

A FastAPI-based backend for an expense tracking and analytics application. The
project provides a layered architecture with API routing, business logic,
data access, and SQLite persistence.

> **Project status:** Early development. The create-expense endpoint is
> functional with full database persistence. Read, update, delete, analytics,
> authentication, and error handling are not yet implemented.

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
|   |   `-- expenses.py             # Expense router (POST /expenses)
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
|   `-- test_health.py              # Health endpoint test
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
  -d '{"amount": "249.99", "category": "Groceries", "description": "Weekly grocery shopping", "expense_date": "2026-09-04"}'
```

Successful response (`201 Created`):

```json
{
  "id": 1,
  "amount": "249.99",
  "category": "Groceries",
  "description": "Weekly grocery shopping",
  "expense_date": "2026-09-04"
}
```

## Expense schemas

The models in `app/schemas/expense.py` define request and response validation
for expense endpoints.

### `ExpenseCreate`

| Field | Type | Validation |
| --- | --- | --- |
| `amount` | Decimal | Must be greater than `0`, max 12 digits, 2 decimal places |
| `category` | String | Between 1 and 50 characters |
| `description` | String | Between 1 and 255 characters |
| `expense_date` | Date | ISO 8601 date, such as `2026-09-04` |

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

The current test suite verifies that `GET /health` returns status code `200` and
the expected JSON response.

## Configuration and persistence

The application uses SQLite with the database file `expenses.db` at the project
root. The table is created automatically on startup via `initialize_database()`.
`.env` files and `*.db` files are ignored by Git.

No environment variables are required. The database path is resolved relative to
the project root in `app/db/database.py`.

## Current development roadmap

Likely next steps for the API are:

1. Add `GET /expenses` (list all) and `GET /expenses/{id}` (get one) endpoints.
2. Add `PUT /expenses/{id}` (update) and `DELETE /expenses/{id}` (delete) endpoints.
3. Add filtering, sorting, and aggregation for expense analytics.
4. Add consistent error handling and custom exception responses.
5. Add CORS middleware and environment-based configuration.
6. Expand unit and integration test coverage.
7. Add authentication and authorization if expenses are user-specific.

## License

No license file is currently included. Add one before distributing or accepting
external contributions to clarify permitted use.
