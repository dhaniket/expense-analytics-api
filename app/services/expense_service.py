from datetime import date

from fastapi import HTTPException, params

from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseCreate

from typing import Literal

from app.errors.expense_errors import (
    ExpenseNotFoundError,
    InvalidExpenseDateRangeError,
)
from dataclasses import replace

from app.schemas.expense import (
    ExpenseUpdate,
)


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

        expense = self.repository.get_by_id(expense_id)
        if not expense:
            raise ExpenseNotFoundError(expense_id=expense_id)

        return expense

    def list_expenses(
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

        if start_date is not None and end_date is not None and start_date > end_date:
            raise InvalidExpenseDateRangeError(start_date=start_date, end_date=end_date)

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
    ) -> None:

        deleted = self.repository.delete(expense_id)

        if not deleted:
            raise ExpenseNotFoundError(expense_id)

    def update_expense(
        self,
        expense_id: int,
        update_data: ExpenseUpdate,
    ) -> Expense:

        existing_expense = self.get_expense(expense_id)

        changes = update_data.model_dump(exclude_unset=True)

        updated_expense = replace(
            existing_expense,
            **changes,
        )

        saved_expense = self.repository.update(updated_expense)

        if saved_expense is None:
            raise ExpenseNotFoundError(expense_id)

        return saved_expense
