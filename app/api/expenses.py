from fastapi import APIRouter, status

from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.services.expense_service import ExpenseService

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


repository = ExpenseRepository()
service = ExpenseService(repository)


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    expense_data: ExpenseCreate,
) -> ExpenseResponse:

    expense = service.create_expense(expense_data)

    return ExpenseResponse.model_validate(expense)
