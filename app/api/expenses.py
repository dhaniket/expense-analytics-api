from datetime import date

from typing import Annotated

from fastapi import (
    APIRouter,
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

from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
)

from app.api.dependencies import (
    ExpenseServiceDep,
)

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    expense_data: ExpenseCreate, service: ExpenseServiceDep
) -> ExpenseResponse:

    expense = service.create_expense(expense_data)

    return ExpenseResponse.model_validate(expense)


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def get_expense(
    expense_id: Annotated[int, Path(gt=0)], service: ExpenseServiceDep
) -> ExpenseResponse:

    expense = service.get_expense(expense_id)

    return ExpenseResponse.model_validate(expense)


@router.get(
    "",
    response_model=PaginatedResponse[ExpenseResponse],
)
def list_expenses(
    params: Annotated[ExpenseQueryParams, Query()], service: ExpenseServiceDep
) -> PaginatedResponse[ExpenseResponse]:

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
    expense_id: Annotated[int, Path(gt=0)], service: ExpenseServiceDep
) -> Response:

    service.delete_expense(expense_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
