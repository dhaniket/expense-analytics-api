CREATE INDEX idx_expenses_expense_date
ON expenses (
    expense_date
);

CREATE INDEX idx_expenses_category_expense_date
ON expenses (
    category,
    expense_date DESC
);