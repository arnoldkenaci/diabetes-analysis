from fastapi import APIRouter

from .endpoints import diabetes, health, users

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(diabetes.router, prefix="/diabetes", tags=["diabetes"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
