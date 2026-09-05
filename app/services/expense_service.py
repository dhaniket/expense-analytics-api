from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseCreate


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
