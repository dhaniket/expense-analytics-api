from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    category: str = Field(
        min_length=1,
        max_length=50,
    )

    description: str = Field(
        min_length=1,
        max_length=255,
    )

    expense_date: date


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category: str
    description: str
    expense_date: date
