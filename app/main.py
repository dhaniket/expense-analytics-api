from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.expenses import router as expenses_router
from app.db.database import initialize_database
from app.api.router import api_router
from app.errors.handlers import (
    register_exception_handlers,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()

    yield


app = FastAPI(
    title="Expense Analytics API",
    version="1.0.0",
    lifespan=lifespan,
)
register_exception_handlers(app)

app.include_router(api_router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
