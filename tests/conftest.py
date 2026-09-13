import os

import psycopg
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()


from app.main import app


@pytest.fixture
def test_database_url() -> str:

    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:

        pytest.fail("TEST_DATABASE_URL " "is not configured")

    main_database_url = os.getenv("DATABASE_URL")

    if main_database_url and database_url == main_database_url:

        pytest.fail("TEST_DATABASE_URL must " "not be DATABASE_URL")

    return database_url


def reset_database(
    database_url: str,
) -> None:

    with psycopg.connect(database_url) as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                TRUNCATE TABLE expenses
                RESTART IDENTITY;
                """)


@pytest.fixture
def clean_test_database(
    test_database_url: str,
):

    reset_database(test_database_url)

    yield

    reset_database(test_database_url)


@pytest.fixture
def client(
    monkeypatch,
    test_database_url: str,
    clean_test_database,
):

    monkeypatch.setenv(
        "DATABASE_URL",
        test_database_url,
    )

    app.dependency_overrides.clear()

    with TestClient(app) as test_client:

        yield test_client

    app.dependency_overrides.clear()
