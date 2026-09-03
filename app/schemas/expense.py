from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=255)
    expense_date: date


class ExpenseResponse(BaseModel):
    id: int
    amount: Decimal
    category: str
    description: str
    expense_date: date
