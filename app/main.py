from fastapi import FastAPI

from app.api.expenses import router as expenses_router
from app.db.database import initialize_database

initialize_database()


app = FastAPI(
    title="Expense Analytics API",
    version="1.0.0",
)


app.include_router(expenses_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
