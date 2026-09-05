from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.expenses import router as expenses_router
from app.db.database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()

    yield


app = FastAPI(
    title="Expense Analytics API",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(expenses_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
