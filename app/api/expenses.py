from datetime import date

from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from app.schemas.common import (
    PaginatedResponse,
)
from app.schemas.expense_query import (
    ExpenseQueryParams,
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
    response_model=PaginatedResponse[ExpenseResponse],
)
def list_expenses(
    params: Annotated[ExpenseQueryParams, Query()],
) -> list[ExpenseResponse]:

    if (
        params.start_date is not None
        and params.end_date is not None
        and params.start_date > params.end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("start_date cannot be " "after end_date"),
        )

    expenses = service.list_expenses(
        category=params.category,
        start_date=params.start_date,
        end_date=params.end_date,
        limit=params.limit,
        offset=params.offset,
        sort_by=params.sort_by,
        sort_order=params.sort_order,
    )

    return PaginatedResponse[ExpenseResponse](
        items=[ExpenseResponse.model_validate(expense) for expense in expenses],
        limit=params.limit,
        offset=params.offset,
    )


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
