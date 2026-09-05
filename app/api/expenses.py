from datetime import date

from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)

from app.repositories.expense_repository import (
    ExpenseRepository,
)
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
)
from app.services.expense_service import (
    ExpenseService,
)

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


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def get_expense(
    expense_id: int = Path(gt=0),
) -> ExpenseResponse:

    expense = service.get_expense(expense_id)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return ExpenseResponse.model_validate(expense)


@router.get(
    "",
    response_model=list[ExpenseResponse],
)
def list_expenses(
    category: str | None = Query(
        default=None,
        min_length=1,
        max_length=50,
    ),
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[ExpenseResponse]:

    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("start_date cannot be " "after end_date"),
        )

    expenses = service.list_expenses(
        category=category,
        start_date=start_date,
        end_date=end_date,
    )

    return [ExpenseResponse.model_validate(expense) for expense in expenses]


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(
    expense_id: int = Path(gt=0),
) -> Response:

    deleted = service.delete_expense(expense_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
