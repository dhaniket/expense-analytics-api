# Expense Analytics API

A production-style backend API built with **Python, FastAPI, Pydantic, SQLite, Uvicorn, and pytest**.

The project demonstrates clean backend architecture, REST API design, dependency injection, validation, persistence, structured error handling, partial updates, pagination, filtering, sorting, OpenAPI documentation, and automated testing.

The focus is not only on making endpoints work, but on structuring the backend so it is easier to test, maintain, and evolve.

---

## Features

- Create expenses
- Fetch an expense by ID
- List expenses
- Partially update expenses with `PATCH`
- Delete expenses
- Filter by category
- Filter by date range
- Sort by supported fields
- Sort ascending or descending
- Limit/offset pagination
- API versioning with `/api/v1`
- Strict request validation
- Structured domain error responses
- Dependency injection with FastAPI `Depends`
- SQLite persistence
- Decimal-based money handling
- Integer paise storage internally
- Automatic OpenAPI / Swagger documentation
- API integration tests
- Service-layer unit tests
- Regression tests for previously discovered bugs

---

## Tech Stack

- Python 3.13+
- FastAPI
- Pydantic
- SQLite
- Uvicorn
- pytest
- Starlette TestClient
- Git

---

## API Endpoints

| Method | Endpoint | Description | Success |
|---|---|---|---:|
| `GET` | `/health` | Health check | `200` |
| `POST` | `/api/v1/expenses` | Create an expense | `201` |
| `GET` | `/api/v1/expenses` | List/filter/sort/paginate expenses | `200` |
| `GET` | `/api/v1/expenses/{expense_id}` | Fetch one expense | `200` |
| `PATCH` | `/api/v1/expenses/{expense_id}` | Partially update an expense | `200` |
| `DELETE` | `/api/v1/expenses/{expense_id}` | Delete an expense | `204` |

---

## Architecture

```text
External HTTP Request
        │
        ▼
Pydantic Validation
        │
        ▼
FastAPI Router
        │
        ▼
Injected ExpenseService
        │
        ▼
Business Rules
        │
        ▼
ExpenseRepository
        │
        ▼
SQLite
```

Error flow:

```text
Domain Failure
      │
      ▼
Domain Exception
      │
      ▼
Global Exception Handler
      │
      ▼
Structured HTTP Error
```

Testing:

```text
API Tests
→ HTTP + FastAPI + Service + Repository + SQLite

Service Tests
→ Service + Fake Repository
```

---

## Layer Responsibilities

### Router Layer

Responsible for HTTP concerns:

- route definitions
- request parsing
- query parameters
- path parameters
- response models
- HTTP status codes
- dependency injection

The router does not contain SQL or core business rules.

### Service Layer

Responsible for application and business rules:

- create expense
- get expense
- list expenses
- validate date ranges
- partial-update behavior
- delete behavior
- interpret repository results
- raise domain exceptions when required

Example:

```text
Repository returns None
        ↓
Service interprets it
        ↓
ExpenseNotFoundError
```

### Repository Layer

Responsible for persistence:

- SQL queries
- inserts
- selects
- updates
- deletes
- filtering
- sorting
- pagination
- converting database rows into domain objects

The repository does not know about HTTP status codes.

---

## Dependency Injection

FastAPI dependencies are used to construct and inject the repository and service.

Conceptually:

```text
FastAPI
   │
   ▼
get_expense_repository()
   │
   ▼
ExpenseRepository
   │
   ▼
get_expense_service(repository)
   │
   ▼
ExpenseService
   │
   ▼
Endpoint
```

Example:

```python
ExpenseServiceDep = Annotated[
    ExpenseService,
    Depends(get_expense_service),
]
```

This reduces coupling and makes dependencies easier to replace during tests.

---

## Domain Errors

The service layer raises application-specific exceptions instead of FastAPI `HTTPException`.

Examples:

```python
ExpenseNotFoundError
InvalidExpenseDateRangeError
```

Global exception handlers translate these domain failures into HTTP responses.

### Missing expense

```json
{
  "error": {
    "code": "EXPENSE_NOT_FOUND",
    "message": "Expense 99999 not found"
  }
}
```

### Invalid date range

```json
{
  "error": {
    "code": "INVALID_DATE_RANGE",
    "message": "start_date cannot be after end_date"
  }
}
```

This gives API consumers a predictable error contract.

---

## Validation vs Business Rules

The project distinguishes schema validation from business-level validation.

### Request validation

Examples:

```text
limit=1000
```

or:

```json
{
  "amount": "-1.00"
}
```

These are rejected by FastAPI/Pydantic with:

```text
422 Unprocessable Entity
```

### Business validation

Example:

```text
start_date=2026-09-10
end_date=2026-09-01
```

Both values are individually valid dates, but the combination is invalid.

The service raises:

```python
InvalidExpenseDateRangeError
```

and the API returns:

```text
400 Bad Request
```

---

## Query Parameters

`GET /api/v1/expenses` supports:

```text
category
start_date
end_date
limit
offset
sort_by
sort_order
```

Example:

```text
GET /api/v1/expenses?category=Food&limit=10&offset=0&sort_by=amount&sort_order=desc
```

Unknown query parameters are rejected using:

```python
ConfigDict(
    extra="forbid"
)
```

This prevents typos such as:

```text
?limmit=10
```

from being silently ignored.

---

## Pagination

The API uses limit/offset pagination.

Example:

```text
GET /api/v1/expenses?limit=20&offset=0
```

Response:

```json
{
  "items": [],
  "limit": 20,
  "offset": 0
}
```

A reusable generic response model is used:

```python
PaginatedResponse[ExpenseResponse]
```

The API also limits the maximum allowed page size to avoid unbounded requests.

---

## Sorting

Supported sort fields are explicitly whitelisted:

```text
id
expense_date
amount
```

Supported sort orders:

```text
asc
desc
```

Repository whitelist:

```python
sort_columns = {
    "id": "id",
    "expense_date": "expense_date",
    "amount": "amount_paise",
}
```

This prevents arbitrary client-controlled SQL identifiers from being inserted into queries.

---

## SQL Safety

Dynamic values are passed as SQL parameters:

```sql
WHERE category = ?
LIMIT ?
OFFSET ?
```

Sortable column names are selected only from the application-controlled whitelist.

---

## Partial Updates with PATCH

The API supports:

```http
PATCH /api/v1/expenses/{expense_id}
```

Example:

```json
{
  "amount": "300.00"
}
```

Only the supplied field changes.

Other fields remain unchanged.

The implementation uses:

```python
update_data.model_dump(
    exclude_unset=True
)
```

to distinguish between fields that were omitted and fields that were explicitly supplied.

---

## PATCH Semantics

For this API:

```text
Field omitted
→ keep existing value

Field supplied
→ validate and update
```

Required domain fields cannot be explicitly changed to `null`.

The API also rejects an empty PATCH body:

```json
{}
```

because a partial update must request at least one actual change.

The service uses:

```python
dataclasses.replace(...)
```

to create an updated domain object while preserving fields that were not changed.

---

## PUT vs PATCH

This API intentionally implements `PATCH`, not `PUT`.

### PATCH

Used for partial modification:

```json
{
  "category": "Travel"
}
```

Only the category changes.

### PUT

Normally represents full-resource replacement semantics.

Since this API requires partial field modification, `PATCH` is the appropriate choice.

---

## HTTP Semantics

The API uses:

```text
200 OK
→ successful GET / PATCH

201 Created
→ successful POST

204 No Content
→ successful DELETE

400 Bad Request
→ invalid business-level request relationship

404 Not Found
→ resource does not exist

422 Unprocessable Entity
→ request validation failure
```

The project also covers REST concepts such as safe methods and idempotency.

---

## Money Handling

Money is represented using Python `Decimal` rather than floating-point numbers.

SQLite stores amounts internally as integer paise:

```text
₹250.00
→ 25000
```

Database reads normalize amounts back to two decimal places:

```text
30000
→ Decimal("300.00")
```

This avoids floating-point precision issues and keeps monetary output consistent.

---

## Example Create Request

```http
POST /api/v1/expenses
```

```json
{
  "amount": "450.00",
  "category": "Food",
  "description": "Dinner",
  "expense_date": "2026-09-10"
}
```

Example response:

```json
{
  "id": 1,
  "amount": "450.00",
  "category": "Food",
  "description": "Dinner",
  "expense_date": "2026-09-10"
}
```

---

## Example PATCH Request

```http
PATCH /api/v1/expenses/1
```

```json
{
  "amount": "500.00"
}
```

Example response:

```json
{
  "id": 1,
  "amount": "500.00",
  "category": "Food",
  "description": "Dinner",
  "expense_date": "2026-09-10"
}
```

---

## Project Structure

```text
expense-analytics-api/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── expenses.py
│   │   └── router.py
│   │
│   ├── db/
│   │   └── database.py
│   │
│   ├── errors/
│   │   ├── __init__.py
│   │   ├── expense_errors.py
│   │   └── handlers.py
│   │
│   ├── models/
│   │   └── expense.py
│   │
│   ├── repositories/
│   │   └── expense_repository.py
│   │
│   ├── schemas/
│   │   ├── common.py
│   │   ├── error.py
│   │   ├── expense.py
│   │   └── expense_query.py
│   │
│   ├── services/
│   │   └── expense_service.py
│   │
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_expenses.py
│   └── test_expense_service.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── ...
```

Exact filenames may vary slightly depending on local organization.

---

## Running the Application

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

Application:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

---

## Health Check

```http
GET /health
```

Expected:

```json
{
  "status": "ok"
}
```

---

## Running Tests

Run the complete test suite:

```powershell
pytest -v
```

or:

```powershell
pytest -q
```

---

## Testing Strategy

### API / Integration Tests

These exercise:

```text
TestClient
   ↓
FastAPI
   ↓
Service
   ↓
Repository
   ↓
Temporary SQLite database
```

They cover:

- create
- get
- list
- filters
- sorting
- pagination
- PATCH
- delete
- validation errors
- structured errors
- OpenAPI contract

### Service Unit Tests

These test:

```text
ExpenseService
      ↓
FakeExpenseRepository
```

without HTTP or SQLite.

They verify business rules such as:

- missing expense behavior
- invalid date ranges
- partial-update field preservation
- delete-missing behavior

---

## Dependency Overrides

FastAPI dependency overrides can replace real dependencies during tests.

Conceptually:

```text
Real ExpenseService
        ↓ replaced with
Stub / Fake ExpenseService
```

This allows HTTP behavior to be tested independently from the real persistence layer.

---

## Test Isolation

Tests use a temporary database rather than the development database.

The test setup uses:

```text
pytest fixtures
tmp_path
monkeypatch
TestClient
```

This prevents automated tests from changing real application data.

---

## Contract and Edge-Case Tests

The suite covers cases such as:

- invalid expense IDs
- invalid sort order
- unsupported sort fields
- unknown query parameters
- unknown PATCH fields
- empty PATCH bodies
- null values for required fields
- DELETE returning an empty `204` body
- pagination offsets
- structured `404` responses
- invalid date ranges
- generated OpenAPI routes

---

## Regression Testing

A regression test protects money formatting after a bug was found where:

```text
300.00
```

could be returned as:

```text
300
```

after a database round trip.

The conversion was fixed and the behavior is now locked by automated tests.

The general workflow is:

```text
Bug discovered
      ↓
Root cause identified
      ↓
Fix applied
      ↓
Regression test added
```

---

## OpenAPI and Swagger

FastAPI automatically generates OpenAPI documentation from:

- route definitions
- request schemas
- query models
- response models
- documented error responses

Relevant `400` and `404` responses use the shared `ErrorResponse` model.

Tests also verify that the expense paths and PATCH operation are present in:

```text
/openapi.json
```

---

## Key Engineering Concepts Demonstrated

### Python

- type hints
- dataclasses
- `Decimal`
- `date`
- context managers
- custom exceptions
- `Literal`
- `Annotated`
- `TypeVar`
- generics
- duck typing
- `dataclasses.replace`

### FastAPI

- `FastAPI`
- `APIRouter`
- router composition
- API versioning
- `Depends`
- dependency injection
- `Annotated`
- `Query`
- `Path`
- request models
- response models
- lifespan
- custom exception handlers
- dependency overrides
- OpenAPI
- Swagger
- response documentation

### Pydantic

- request schemas
- response schemas
- query parameter models
- `Field`
- `ConfigDict`
- `extra="forbid"`
- validation constraints
- model validators
- `model_dump(exclude_unset=True)`

### REST / API Design

- resource-oriented URLs
- API versioning
- pagination
- filtering
- sorting
- `GET`
- `POST`
- `PATCH`
- `DELETE`
- `PUT` vs `PATCH`
- safe methods
- idempotency
- status-code semantics
- structured error contracts

### Backend Architecture

```text
Router
→ HTTP concerns

Service
→ business rules

Repository
→ persistence

Database
→ storage
```

Also demonstrated:

- dependency injection
- separation of concerns
- domain exceptions
- centralized error translation
- fake repositories
- dependency substitution
- regression protection

---

## Why Use Multiple Layers?

A small application could put SQL directly inside FastAPI route functions.

This project intentionally separates:

```text
Router
→ Service
→ Repository
```

because it improves:

- separation of concerns
- testability
- business-logic reuse
- database replaceability
- maintainability
- framework independence

---

## Current Limitations

The project intentionally does not yet include:

- PostgreSQL
- database migrations
- authentication
- authorization
- Redis
- caching
- Kafka
- RabbitMQ
- Docker
- Kubernetes
- distributed processing
- production monitoring
- cursor pagination
- total-count pagination metadata

---

## Possible Future Improvements

Potential next improvements include:

- migrate persistence to PostgreSQL
- add schema migrations
- add indexes for common filters and sorting
- return pagination totals
- introduce authentication and authorization
- add structured logging
- add production monitoring and observability
- containerize the application
- add CI/CD
- add caching where justified

---

## What This Project Demonstrates

This project demonstrates more than basic FastAPI syntax.

It shows how to build a backend with:

- explicit API contracts
- strict input validation
- separated application layers
- dependency injection
- reusable business logic
- isolated persistence logic
- consistent domain error handling
- correct REST semantics
- partial-update behavior
- SQL safety
- automated integration tests
- service-level unit tests
- fake dependencies
- regression protection
- generated API documentation

It provides a solid foundation for evolving the service into a larger production backend.
