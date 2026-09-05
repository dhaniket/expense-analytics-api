from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Expense:
    id: int
    amount: Decimal
    category: str
    description: str
    expense_date: date
