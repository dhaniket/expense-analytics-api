import pytest
from fastapi.testclient import TestClient

from app.db import database
from app.main import app


@pytest.fixture
def client(
    tmp_path,
    monkeypatch,
):
    test_db_path = tmp_path / "test_expenses.db"

    monkeypatch.setattr(
        database,
        "DB_PATH",
        test_db_path,
    )

    with TestClient(app) as test_client:
        yield test_client
