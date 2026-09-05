from datetime import date
from decimal import Decimal

from app.db.database import get_connection
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate


class ExpenseRepository:

    def create(self, expense_data: ExpenseCreate) -> Expense:
        amount_paise = int(expense_data.amount * Decimal("100"))

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO expenses (
                    amount_paise,
                    category,
                    description,
                    expense_date
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    amount_paise,
                    expense_data.category,
                    expense_data.description,
                    expense_data.expense_date.isoformat(),
                ),
            )

            expense_id = cursor.lastrowid

        return Expense(
            id=expense_id,
            amount=expense_data.amount,
            category=expense_data.category,
            description=expense_data.description,
            expense_date=expense_data.expense_date,
        )

    def get_by_id(
        self,
        expense_id: int,
    ) -> Expense | None:

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    amount_paise,
                    category,
                    description,
                    expense_date
                FROM expenses
                WHERE id = ?
                """,
                (expense_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_expense(row)

    def list(
        self,
        category: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
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

        conditions = []
        parameters = []

        if category is not None:
            conditions.append("category = ?")
            parameters.append(category)

        if start_date is not None:
            conditions.append("expense_date >= ?")
            parameters.append(start_date.isoformat())

        if end_date is not None:
            conditions.append("expense_date <= ?")
            parameters.append(end_date.isoformat())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY expense_date DESC, id DESC"

        with get_connection() as connection:
            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [self._row_to_expense(row) for row in rows]

    def delete(
        self,
        expense_id: int,
    ) -> bool:

        with get_connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM expenses
                WHERE id = ?
                """,
                (expense_id,),
            )

            deleted = cursor.rowcount > 0

        return deleted

    @staticmethod
    def _row_to_expense(row) -> Expense:
        amount = Decimal(row["amount_paise"]) / Decimal("100")

        return Expense(
            id=row["id"],
            amount=amount,
            category=row["category"],
            description=row["description"],
            expense_date=date.fromisoformat(row["expense_date"]),
        )
