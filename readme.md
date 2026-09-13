# Expense Analytics API

A production-oriented REST API for managing and querying expenses, built with **Python, FastAPI, Pydantic, Psycopg, Neon PostgreSQL, and pytest**.

The project demonstrates clean backend architecture, PostgreSQL schema design, strict validation, dependency injection, structured error handling, partial updates, filtering, sorting, pagination, database constraints, indexing, transaction safety, OpenAPI documentation, and isolated automated testing.

---

## Features

- Create expenses
- Fetch an expense by ID
- List expenses
- Partially update expenses with `PATCH`
- Delete expenses
- Filter by category
- Filter by date range
- Sort by:
  - `id`
  - `expense_date`
  - `amount`
- Ascending and descending sorting
- Limit/offset pagination
- API versioning under `/api/v1`
- Strict query and body validation
- Structured domain error responses
- PostgreSQL persistence through Psycopg
- Neon-hosted PostgreSQL
- Integer-paise money storage
- PostgreSQL constraints for data integrity
- Query indexes for common access patterns
- Transaction-based commit/rollback behavior
- OpenAPI / Swagger documentation
- Service-layer unit tests
- API integration tests
- Database constraint tests
- Isolated Neon test database branch

---

## Tech Stack

- Python 3.13+
- FastAPI
- Pydantic
- Psycopg 3
- PostgreSQL
- Neon
- Uvicorn
- pytest
- Starlette TestClient
- python-dotenv
- Git

---

## API Endpoints

| Method | Endpoint | Description | Success |
|---|---|---|---:|
| `GET` | `/health` | Application health check | `200` |
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
Psycopg
        │
        ▼
Neon PostgreSQL
```

### Error flow

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

### Testing layers

```text
Service Unit Tests
ExpenseService
      ↓
FakeExpenseRepository
```

```text
API Integration Tests
TestClient
    ↓
FastAPI
    ↓
ExpenseService
    ↓
ExpenseRepository
    ↓
Neon test branch
```

```text
Database Tests
Psycopg
   ↓
Neon test branch
   ↓
PostgreSQL constraints
```

---

## Layer Responsibilities

### Router

Responsible for HTTP-specific concerns:

- routes
- query parameters
- path parameters
- request bodies
- response models
- status codes
- dependency injection

The router does not contain SQL or persistence logic.

### Service

Responsible for application and business rules:

- create expense
- retrieve expense
- list expenses
- validate date ranges
- partial-update behavior
- delete behavior
- translate repository outcomes into domain outcomes

The service raises domain exceptions instead of framework-specific HTTP exceptions.

### Repository

Responsible for PostgreSQL persistence:

- parameterized SQL
- inserts
- selects
- updates
- deletes
- filtering
- sorting
- pagination
- row-to-domain mapping
- money conversion

---

## Dependency Injection

FastAPI constructs the repository and service through dependencies.

Conceptually:

```text
get_expense_repository()
          │
          ▼
   ExpenseRepository
          │
          ▼
get_expense_service(...)
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

This keeps route handlers decoupled from dependency construction and allows test dependencies to be substituted when needed.

---

## PostgreSQL Schema

The database schema is defined in:

```text
sql/001_create_expenses.sql
```

The `expenses` table contains:

```text
id
amount_paise
category
description
expense_date
created_at
updated_at
```

Key schema choices:

- `BIGINT GENERATED ALWAYS AS IDENTITY` for IDs
- `BIGINT` for integer paise
- `VARCHAR(50)` for category
- `VARCHAR(255)` for description
- `DATE` for expense dates
- `TIMESTAMPTZ` for audit timestamps

### Data integrity constraints

PostgreSQL enforces:

```text
amount_paise > 0
category must not be blank
description must not be blank
required columns must not be NULL
```

This gives the application multiple validation boundaries:

```text
Pydantic
→ request validation

ExpenseService
→ business rules

PostgreSQL
→ persisted-data integrity
```

---

## Money Handling

Money is represented in Python with `Decimal`.

The database stores money as integer paise.

```text
₹275.50
   ↓
27550 paise
```

This avoids binary floating-point precision problems.

When values are read from PostgreSQL, they are normalized back to two decimal places.

Conceptually:

```python
(
    Decimal(amount_paise)
    / Decimal("100")
).quantize(
    Decimal("0.01")
)
```

So:

```text
30000
→ Decimal("300.00")
```

---

## PostgreSQL Access with Psycopg

Database configuration is supplied through:

```env
DATABASE_URL=postgresql://...
```

The application connects using Psycopg with dictionary-style rows.

Conceptually:

```python
with psycopg.connect(
    database_url,
    row_factory=dict_row,
) as connection:
    ...
```

PostgreSQL parameters use Psycopg placeholders:

```sql
WHERE id = %s
```

Values are passed separately to `execute()`.

Client values are never concatenated directly into SQL.

---

## PostgreSQL `RETURNING`

PostgreSQL `RETURNING` is used for write operations where the affected row is needed immediately.

Example:

```sql
INSERT INTO expenses (
    amount_paise,
    category,
    description,
    expense_date
)
VALUES (
    %s,
    %s,
    %s,
    %s
)
RETURNING
    id,
    amount_paise,
    category,
    description,
    expense_date;
```

The repository also uses `RETURNING` for update and delete operations.

This avoids unnecessary follow-up queries.

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
GET /api/v1/expenses?category=Food&start_date=2026-09-01&end_date=2026-09-30&limit=20&offset=0&sort_by=expense_date&sort_order=desc
```

Unknown query parameters are rejected rather than silently ignored.

For example:

```text
?limmit=20
```

returns a validation error.

---

## Pagination

The API uses limit/offset pagination.

Example:

```text
GET /api/v1/expenses?limit=20&offset=0
```

Response shape:

```json
{
  "items": [],
  "limit": 20,
  "offset": 0
}
```

A reusable generic pagination model is used:

```python
PaginatedResponse[ExpenseResponse]
```

Limit/offset pagination is intentionally kept simple for the current API. For very large offsets, cursor/keyset pagination would be a possible future improvement.

---

## Sorting and SQL Safety

Supported sort fields are explicitly whitelisted:

```python
sort_columns = {
    "id": "id",
    "expense_date": "expense_date",
    "amount": "amount_paise",
}
```

Supported directions:

```text
asc
desc
```

SQL values use Psycopg parameters, while dynamic identifiers are selected only from trusted application mappings.

Arbitrary user input is never inserted directly as a SQL column name.

---

## Query Indexes

Additional indexes are defined in:

```text
sql/002_add_expense_indexes.sql
```

Current indexes:

```sql
CREATE INDEX idx_expenses_expense_date
ON expenses (
    expense_date
);

CREATE INDEX idx_expenses_category_expense_date
ON expenses (
    category,
    expense_date DESC
);

CREATE INDEX idx_expenses_amount_paise
ON expenses (
    amount_paise
);
```

The primary key already creates an index on `id`, so no additional ID index is required.

### Why these indexes?

They correspond to real API access patterns:

```text
expense_date
→ date filtering and date sorting

(category, expense_date DESC)
→ category filtering
→ category + date filtering
→ category/date ordered queries

amount_paise
→ amount sorting

primary key(id)
→ single-resource lookup
→ ID ordering
```

Indexes are deliberately limited to useful query patterns because every additional index also adds storage and write-maintenance cost.

---

## Query Plan Analysis

PostgreSQL query behavior can be inspected with:

```sql
EXPLAIN
SELECT ...;
```

and:

```sql
EXPLAIN (
    ANALYZE,
    BUFFERS
)
SELECT ...;
```

Relevant plan concepts include:

- Sequential Scan
- Index Scan
- Bitmap Index Scan
- Bitmap Heap Scan
- Sort
- Limit
- planner cost
- actual rows
- Planning Time
- Execution Time

Indexes are added based on real access patterns and measured query plans rather than simply indexing every column.

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

Only supplied fields are changed.

The implementation uses:

```python
update_data.model_dump(
    exclude_unset=True
)
```

so omitted fields remain unchanged.

Required domain fields may be omitted during PATCH, but they cannot be explicitly changed to `null`.

An empty PATCH body is rejected.

---

## REST and HTTP Semantics

The API uses resource-oriented routes and standard HTTP behavior.

```text
200 OK
→ successful GET / PATCH

201 Created
→ successful POST

204 No Content
→ successful DELETE

400 Bad Request
→ invalid business-level request

404 Not Found
→ missing resource

422 Unprocessable Entity
→ request validation failure
```

`PATCH` is used rather than `PUT` because updates are partial rather than full-resource replacements.

---

## Structured Error Responses

Domain errors are translated centrally into consistent HTTP responses.

### Expense not found

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

This keeps HTTP concerns out of the service layer while providing a predictable API contract.

---

## Transactions

Psycopg connection contexts provide transaction behavior for repository operations.

Conceptually:

```text
BEGIN
  ↓
SQL operation
  ↓
success
  ↓
COMMIT
```

If an exception escapes the transaction:

```text
BEGIN
  ↓
SQL operation
  ↓
error
  ↓
ROLLBACK
```

This protects atomicity for each repository operation.

The project also verifies rollback behavior explicitly against the PostgreSQL test database.

### Current transaction boundary

Each repository method currently manages its own database connection and transaction.

This is appropriate for the current CRUD operations.

If a future business operation needs several repository calls to succeed or fail as one unit, a shared transaction / Unit of Work would be a natural extension.

---

## Test Isolation

Development and automated tests use separate Neon database branches.

```text
DATABASE_URL
→ development/main Neon branch

TEST_DATABASE_URL
→ isolated Neon test branch
```

The test suite contains a safety check that prevents:

```text
TEST_DATABASE_URL == DATABASE_URL
```

Integration tests reset the test table with:

```sql
TRUNCATE TABLE expenses
RESTART IDENTITY;
```

This keeps tests deterministic and prevents automated tests from modifying development data.

---

## Testing Strategy

### Service unit tests

Service tests use a fake repository:

```text
ExpenseService
      ↓
FakeExpenseRepository
```

These tests require no database and verify business behavior directly.

Examples include:

- missing expense handling
- invalid date ranges
- partial-update field preservation
- delete-missing behavior

### API integration tests

API tests exercise:

```text
TestClient
    ↓
FastAPI
    ↓
ExpenseService
    ↓
ExpenseRepository
    ↓
Neon PostgreSQL test branch
```

They cover:

- create
- get
- list
- filtering
- sorting
- pagination
- PATCH
- delete
- validation
- structured errors
- OpenAPI contract
- money-format regression behavior

### Database tests

Database-level tests connect directly with Psycopg and verify PostgreSQL constraints independently of FastAPI/Pydantic.

For example, a negative `amount_paise` is expected to raise a PostgreSQL check-constraint violation.

---

## Regression Protection

The test suite protects previously discovered edge cases.

One example was money formatting:

```text
300.00
```

could previously become:

```text
300
```

after a database round trip.

Repository conversion now normalizes monetary values to two decimal places, and automated tests prevent the regression from returning.

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
├── sql/
│   ├── 001_create_expenses.sql
│   └── 002_add_expense_indexes.sql
│
├── tests/
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_expenses.py
│   └── test_expense_service.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

Exact filenames may vary slightly depending on local organization.

---

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd expense-analytics-api
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Neon PostgreSQL Setup

### 1. Create a Neon project

Create a PostgreSQL project in Neon and obtain its connection string.

### 2. Configure the development database

Create:

```text
.env
```

with:

```env
DATABASE_URL=postgresql://your-development-connection-string
```

Do not commit `.env`.

### 3. Create the schema

Apply:

```text
sql/001_create_expenses.sql
```

to the development branch/database.

Then apply:

```text
sql/002_add_expense_indexes.sql
```

### 4. Create a test branch

After the schema and indexes exist on the main/development branch, create an isolated Neon branch for automated testing.

Add its URL:

```env
TEST_DATABASE_URL=postgresql://your-test-branch-connection-string
```

Your final `.env` should conceptually contain:

```env
DATABASE_URL=postgresql://development-database
TEST_DATABASE_URL=postgresql://test-database
```

The two values must point to different database environments.

---

## Environment Template

`.env.example` should contain placeholders only:

```env
DATABASE_URL=postgresql://username:password@hostname/database?sslmode=require
TEST_DATABASE_URL=postgresql://username:password@test-hostname/database?sslmode=require
```

Never commit real credentials.

---

## Running the Application

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

Application startup also checks that PostgreSQL is reachable.

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
  "expense_date": "2026-09-13"
}
```

Example response:

```json
{
  "id": 1,
  "amount": "450.00",
  "category": "Food",
  "description": "Dinner",
  "expense_date": "2026-09-13"
}
```

---

## Example List Request

```http
GET /api/v1/expenses?category=Food&sort_by=expense_date&sort_order=desc&limit=20&offset=0
```

Example response shape:

```json
{
  "items": [
    {
      "id": 1,
      "amount": "450.00",
      "category": "Food",
      "description": "Dinner",
      "expense_date": "2026-09-13"
    }
  ],
  "limit": 20,
  "offset": 0
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

Only the amount changes; omitted fields are preserved.

---

## Running Tests

Make sure both environment variables are configured:

```text
DATABASE_URL
TEST_DATABASE_URL
```

Then run:

```powershell
pytest -v
```

or:

```powershell
pytest -q
```

Automated database/API tests use only `TEST_DATABASE_URL`.

---

## OpenAPI and Swagger

FastAPI generates documentation from:

- routes
- Pydantic schemas
- query models
- response models
- documented error responses

The test suite also verifies important OpenAPI paths and operations so accidental route removal is detected.

---

## Key Engineering Concepts Demonstrated

### Python

- type hints
- dataclasses
- `Decimal`
- `date`
- context managers
- custom exceptions
- generics
- `Literal`
- `Annotated`
- `dataclasses.replace`

### FastAPI

- routers
- dependency injection
- response models
- path/query validation
- lifespan
- custom exception handlers
- dependency overrides
- OpenAPI / Swagger

### PostgreSQL

- identity primary keys
- `DATE`
- `TIMESTAMPTZ`
- `NOT NULL`
- `CHECK`
- parameterized SQL
- `RETURNING`
- transactions
- commit / rollback
- B-tree indexes
- composite indexes
- query planning
- `EXPLAIN`
- `EXPLAIN ANALYZE`
- `ANALYZE`
- test-data isolation

### API Design

- versioned REST routes
- filtering
- sorting
- pagination
- partial updates
- HTTP status-code semantics
- structured errors
- strict input contracts

### Testing

- unit tests
- fake repositories
- integration tests
- isolated test database
- database constraint tests
- regression tests
- OpenAPI contract tests

---

## Current Limitations

The project intentionally does not yet include:

- authentication / authorization
- schema migration framework such as Alembic
- connection pooling managed inside the application
- cursor/keyset pagination
- total-count pagination metadata
- Redis caching
- background workers
- message queues
- Docker
- Kubernetes
- production observability

These are natural future extensions rather than requirements for the current scope.

---

## Possible Future Improvements

- introduce Alembic for managed migrations
- add authentication and authorization
- use cursor pagination for very large datasets
- add aggregate analytics endpoints
- add PostgreSQL connection-pool configuration where appropriate
- add structured application logging
- add observability and metrics
- containerize the service
- add CI/CD
- add caching where justified
- introduce a shared transaction / Unit of Work if multi-step atomic business operations are added

---

## Design Principles

The project follows a few deliberate principles:

```text
Validate at the boundary
Protect invariants in the database
Keep HTTP logic out of business logic
Keep SQL out of route handlers
Parameterize SQL values
Whitelist dynamic SQL identifiers
Measure query behavior before adding indexes
Keep tests isolated from development data
Prefer simple architecture until additional complexity is justified
```

The result is a compact API that demonstrates production-oriented backend engineering without introducing infrastructure that the current problem does not require.
