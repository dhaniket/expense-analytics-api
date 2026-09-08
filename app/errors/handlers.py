from fastapi import (
    FastAPI,
    Request,
)
from fastapi.responses import (
    JSONResponse,
)

from app.errors.expense_errors import (
    ExpenseNotFoundError,
    InvalidExpenseDateRangeError,
)
from app.schemas.error import (
    ErrorDetail,
    ErrorResponse,
)


async def expense_not_found_handler(
    request: Request,
    exc: ExpenseNotFoundError,
) -> JSONResponse:

    response = ErrorResponse(
        error=ErrorDetail(
            code="EXPENSE_NOT_FOUND",
            message=str(exc),
        )
    )

    return JSONResponse(
        status_code=404,
        content=response.model_dump(),
    )


async def invalid_date_range_handler(
    request: Request,
    exc: InvalidExpenseDateRangeError,
) -> JSONResponse:

    response = ErrorResponse(
        error=ErrorDetail(
            code="INVALID_DATE_RANGE",
            message=str(exc),
        )
    )

    return JSONResponse(
        status_code=400,
        content=response.model_dump(),
    )


def register_exception_handlers(
    app: FastAPI,
) -> None:

    app.add_exception_handler(
        ExpenseNotFoundError,
        expense_not_found_handler,
    )

    app.add_exception_handler(
        InvalidExpenseDateRangeError,
        invalid_date_range_handler,
    )
