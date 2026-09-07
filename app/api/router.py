from fastapi import APIRouter

# from app.api.analytics import router as analytics_router
from app.api.expenses import router as expenses_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(expenses_router)

# api_router.include_router(analytics_router)
