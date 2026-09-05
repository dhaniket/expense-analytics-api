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
