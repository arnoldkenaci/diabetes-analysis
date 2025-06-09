from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.scheduler import AnalysisScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()

# Global scheduler instance
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global scheduler

    # Create database session
    db = SessionLocal()

    # Initialize scheduler
    scheduler = AnalysisScheduler(db)

    yield

    # Cleanup
    db.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Diabetes Dataset Analysis API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
