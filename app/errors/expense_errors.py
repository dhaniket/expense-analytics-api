from datetime import date


class ExpenseNotFoundError(Exception):

    def __init__(
        self,
        expense_id: int,
    ) -> None:

        self.expense_id = expense_id

        super().__init__(f"Expense {expense_id} not found")


class InvalidExpenseDateRangeError(Exception):

    def __init__(
        self,
        start_date: date,
        end_date: date,
    ) -> None:

        self.start_date = start_date
        self.end_date = end_date

        super().__init__("start_date cannot be after end_date")
