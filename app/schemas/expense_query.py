from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ExpenseQueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    start_date: date | None = None

    end_date: date | None = None

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    offset: int = Field(
        default=0,
        ge=0,
    )

    sort_by: Literal["expense_date", "amount"] = "expense_date"

    sort_order: Literal["asc", "desc"] = "desc"
