import psycopg
import pytest


def test_database_rejects_negative_amount(
    test_database_url: str,
    clean_test_database,
):

    with pytest.raises(psycopg.errors.CheckViolation):

        with psycopg.connect(test_database_url) as connection:

            with connection.cursor() as cursor:

                cursor.execute(
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
                        CURRENT_DATE
                    )
                    """,
                    (
                        -100,
                        "Food",
                        "Invalid expense",
                    ),
                )
