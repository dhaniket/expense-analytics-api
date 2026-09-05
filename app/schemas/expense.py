from datetime import date
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


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

    @field_validator(
        "category",
        "description",
        mode="before",
    )
    @classmethod
    def validate_non_empty_text(
        cls,
        value: str,
    ) -> str:

        if isinstance(value, str):
            value = value.strip()

        if not value:
            raise ValueError("must not be empty")

        return value


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category: str
    description: str
    expense_date: date
