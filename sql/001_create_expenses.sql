CREATE TABLE expenses (
    id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    amount_paise BIGINT
        NOT NULL,

    category VARCHAR(50)
        NOT NULL,

    description VARCHAR(255)
        NOT NULL,

    expense_date DATE
        NOT NULL,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT expenses_amount_positive
        CHECK (
            amount_paise > 0
        ),

    CONSTRAINT expenses_category_not_blank
        CHECK (
            length(trim(category)) > 0
        ),

    CONSTRAINT expenses_description_not_blank
        CHECK (
            length(trim(description)) > 0
        )
);