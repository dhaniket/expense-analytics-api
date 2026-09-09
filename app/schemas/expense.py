from datetime import date
from decimal import Decimal
from typing import Self
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
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


class ExpenseUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    amount: Decimal | None = Field(
        default=None,
        gt=0,
    )

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    expense_date: date | None = None

    @model_validator(mode="after")
    def validate_update(
        self,
    ) -> Self:

        if not self.model_fields_set:
            raise ValueError("At least one field " "must be provided")

        non_nullable_fields = {
            "amount",
            "category",
            "expense_date",
            "description",
        }

        for field_name in non_nullable_fields:
            if (
                field_name in self.model_fields_set
                and getattr(
                    self,
                    field_name,
                )
                is None
            ):
                raise ValueError(f"{field_name} " "cannot be null")

        return self
