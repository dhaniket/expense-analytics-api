from datetime import date
from decimal import Decimal
from typing import Literal

from app.db.database import (
    get_connection,
)
from app.models.expense import Expense
from app.schemas.expense import (
    ExpenseCreate,
)

PAISE_PER_UNIT = Decimal("100")
MONEY_QUANTIZER = Decimal("0.01")


def _amount_to_paise(
    amount: Decimal,
) -> int:

    return int(amount * PAISE_PER_UNIT)


def _paise_to_amount(
    amount_paise: int,
) -> Decimal:

    return (Decimal(amount_paise) / PAISE_PER_UNIT).quantize(MONEY_QUANTIZER)


def _row_to_expense(
    row,
) -> Expense:

    return Expense(
        id=row["id"],
        amount=_paise_to_amount(row["amount_paise"]),
        category=row["category"],
        description=row["description"],
        expense_date=row["expense_date"],
    )


class ExpenseRepository:

    def create(
        self,
        expense_data: ExpenseCreate,
    ) -> Expense:

        amount_paise = _amount_to_paise(expense_data.amount)

        with get_connection() as connection:

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
                        %s
                    )
                    RETURNING
                        id,
                        amount_paise,
                        category,
                        description,
                        expense_date
                    """,
                    (
                        amount_paise,
                        expense_data.category,
                        expense_data.description,
                        expense_data.expense_date,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError("Expense insert failed")

                return _row_to_expense(row)

    def get_by_id(
        self,
        expense_id: int,
    ) -> Expense | None:

        with get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        amount_paise,
                        category,
                        description,
                        expense_date
                    FROM expenses
                    WHERE id = %s
                    """,
                    (expense_id,),
                )

                row = cursor.fetchone()

                if row is None:
                    return None

                return _row_to_expense(row)

    def list(
        self,
        category: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: Literal[
            "id",
            "expense_date",
            "amount",
        ] = "expense_date",
        sort_order: Literal[
            "asc",
            "desc",
        ] = "desc",
    ) -> list[Expense]:

        query = """
            SELECT
                id,
                amount_paise,
                category,
                description,
                expense_date
            FROM expenses
        """

        conditions: list[str] = []
        parameters: list[object] = []

        if category is not None:

            conditions.append("category = %s")

            parameters.append(category)

        if start_date is not None:

            conditions.append("expense_date >= %s")

            parameters.append(start_date)

        if end_date is not None:

            conditions.append("expense_date <= %s")

            parameters.append(end_date)

        if conditions:

            query += " WHERE " + " AND ".join(conditions)

        sort_columns = {
            "id": "id",
            "expense_date": ("expense_date"),
            "amount": "amount_paise",
        }

        sort_column = sort_columns[sort_by]

        sort_direction = "ASC" if sort_order == "asc" else "DESC"

        query += f" ORDER BY " f"{sort_column} " f"{sort_direction}"

        query += " LIMIT %s OFFSET %s"

        parameters.extend(
            [
                limit,
                offset,
            ]
        )

        with get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    parameters,
                )

                rows = cursor.fetchall()

                return [_row_to_expense(row) for row in rows]

    def update(
        self,
        expense: Expense,
    ) -> Expense | None:

        amount_paise = _amount_to_paise(expense.amount)

        with get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE expenses
                    SET
                        amount_paise = %s,
                        category = %s,
                        description = %s,
                        expense_date = %s,
                        updated_at =
                            CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING
                        id,
                        amount_paise,
                        category,
                        description,
                        expense_date
                    """,
                    (
                        amount_paise,
                        expense.category,
                        expense.description,
                        expense.expense_date,
                        expense.id,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    return None

                return _row_to_expense(row)

    def delete(
        self,
        expense_id: int,
    ) -> bool:

        with get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    DELETE FROM expenses
                    WHERE id = %s
                    RETURNING id
                    """,
                    (expense_id,),
                )

                row = cursor.fetchone()

                return row is not None
