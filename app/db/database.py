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
