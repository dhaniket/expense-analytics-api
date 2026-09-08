from typing import Annotated

from fastapi import Depends

from app.repositories.expense_repository import (
    ExpenseRepository,
)
from app.services.expense_service import (
    ExpenseService,
)


def get_expense_repository() -> ExpenseRepository:

    return ExpenseRepository()


ExpenseRepositoryDep = Annotated[
    ExpenseRepository,
    Depends(get_expense_repository),
]


def get_expense_service(
    repository: ExpenseRepositoryDep,
) -> ExpenseService:

    return ExpenseService(repository)


ExpenseServiceDep = Annotated[
    ExpenseService,
    Depends(get_expense_service),
]
