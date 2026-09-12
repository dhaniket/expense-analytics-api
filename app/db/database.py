import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "expenses.db"


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_paise INTEGER NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                expense_date TEXT NOT NULL
            )
            """)


from collections.abc import Generator
from contextlib import contextmanager
import os

import psycopg
from dotenv import load_dotenv
from psycopg import Connection
from psycopg.rows import dict_row

load_dotenv()


def get_database_url() -> str:

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return database_url


@contextmanager
def get_connection() -> Generator[
    Connection,
    None,
    None,
]:

    database_url = get_database_url()

    with psycopg.connect(
        database_url,
        row_factory=dict_row,
    ) as connection:

        yield connection


def check_database_connection() -> None:

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("SELECT 1;")

            cursor.fetchone()
