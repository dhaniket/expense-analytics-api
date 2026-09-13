import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


database_url = os.environ["TEST_DATABASE_URL"]


try:

    with psycopg.connect(database_url) as connection:

        with connection.transaction():

            connection.execute(
                """
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
                """,
                (
                    10000,
                    "Food",
                    "Transaction Test 1",
                    "2026-09-13",
                ),
            )

            connection.execute(
                """
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
                """,
                (
                    20000,
                    "Food",
                    "Transaction Test 2",
                    "2026-09-13",
                ),
            )

            raise RuntimeError("Force rollback")

except RuntimeError:

    print("Transaction rolled back")
