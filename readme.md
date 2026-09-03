# Expense Analytics API

A FastAPI-based backend for an expense tracking and analytics application. The
project currently provides its application foundation, a health-check endpoint,
and Pydantic schemas for expense data.

> **Project status:** Early development. Expense schemas are defined, but expense
> CRUD, persistence, authentication, and analytics endpoints have not been
> implemented yet.

## Technology stack

- Python 3.10 or newer (verified with Python 3.13.5)
- FastAPI
- Pydantic
- Uvicorn
- Pytest and FastAPI TestClient

The repository uses a pinned `requirements.txt` so that local environments can
install the same dependency versions.

## Project structure

```text
expense-analytics-api/
|-- app/
|   |-- __init__.py
|   |-- main.py                 # FastAPI application and routes
|   `-- schemas/
|       |-- __init__.py
|       `-- expense.py          # Expense request and response models
|-- tests/
|   |-- __init__.py
|   `-- test_health.py          # Health endpoint test
|-- .gitignore
|-- requirements.txt
`-- readme.md
```

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

## Available endpoint

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

## Expense schemas

The models in `app/schemas/expense.py` describe the intended shape of future
expense endpoints. They are not connected to an API route yet.

### `ExpenseCreate`

| Field | Type | Validation |
| --- | --- | --- |
| `amount` | Decimal | Must be greater than `0` |
| `category` | String | Between 1 and 50 characters |
| `description` | String | Between 1 and 255 characters |
| `expense_date` | Date | ISO 8601 date, such as `2026-09-04` |

Example payload:

```json
{
  "amount": "249.99",
  "category": "Groceries",
  "description": "Weekly grocery shopping",
  "expense_date": "2026-09-04"
}
```

### `ExpenseResponse`

The response schema contains all `ExpenseCreate` fields plus an integer `id`.
Using `Decimal` for monetary values avoids the rounding behavior associated with
binary floating-point numbers.

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

The application currently requires no environment variables and has no database
connection. `.env` files and local `*.db` files are ignored by Git in preparation
for future configuration and persistence work.

## Current development roadmap

Likely next steps for the API are:

1. Add a database layer and migrations.
2. Implement expense create, read, update, and delete endpoints.
3. Add filtering and aggregation for expense analytics.
4. Add consistent error handling and response schemas.
5. Expand unit and integration test coverage.
6. Add authentication and authorization if expenses are user-specific.

## License

No license file is currently included. Add one before distributing or accepting
external contributions to clarify permitted use.
