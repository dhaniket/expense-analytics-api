from datetime import date

from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseCreate

from typing import Literal


class ExpenseService:

    def __init__(
        self,
        repository: ExpenseRepository,
    ) -> None:
        self.repository = repository

    def create_expense(
        self,
        expense_data: ExpenseCreate,
    ) -> Expense:

        return self.repository.create(expense_data)

    def get_expense(
        self,
        expense_id: int,
    ) -> Expense | None:

        return self.repository.get_by_id(expense_id)

    def list_expenses(
        self,
        category: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: Literal[
            "expense_date",
            "amount",
        ] = "expense_date",
        sort_order: Literal[
            "asc",
            "desc",
        ] = "desc",
    ) -> list[Expense]:

        return self.repository.list(
            category=category,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def delete_expense(
        self,
        expense_id: int,
    ) -> bool:

        return self.repository.delete(expense_id)
