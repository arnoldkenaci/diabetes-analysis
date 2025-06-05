from fastapi import APIRouter
from .endpoints import data, analyze, insights

api_router = APIRouter()

api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
