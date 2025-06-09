from app.api.v1.endpoints import analyze as analyze_router
from app.api.v1.endpoints import data as data_router
from app.api.v1.endpoints import insights as insights_router
from fastapi import APIRouter

api_router = APIRouter()


api_router.include_router(data_router.router, prefix="/data")
api_router.include_router(insights_router.router, prefix="/insights")
api_router.include_router(analyze_router.router, prefix="/analyze")
