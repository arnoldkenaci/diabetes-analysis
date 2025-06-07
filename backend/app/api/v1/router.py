from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_session
from app.services.analysis import AnalysisService

api_router = APIRouter()
analysis_service = AnalysisService(db=get_session())


@api_router.get("/data")
async def get_data(
    db: Session = Depends(get_session),
    min_age: Optional[int] = Query(None, description="Minimum age filter"),
    max_age: Optional[int] = Query(None, description="Maximum age filter"),
    min_bmi: Optional[float] = Query(None, description="Minimum BMI filter"),
    max_bmi: Optional[float] = Query(None, description="Maximum BMI filter"),
    min_glucose: Optional[float] = Query(
        None, description="Minimum glucose level filter"
    ),
    max_glucose: Optional[float] = Query(
        None, description="Maximum glucose level filter"
    ),
    outcome: Optional[bool] = Query(None, description="Filter by diabetes outcome"),
):
    """Get diabetes dataset with optional filters."""
    analysis_service.db = db
    return await analysis_service.get_filtered_data(
        min_age=min_age,
        max_age=max_age,
        min_bmi=min_bmi,
        max_bmi=max_bmi,
        min_glucose=min_glucose,
        max_glucose=max_glucose,
        outcome=outcome,
    )


@api_router.get("/analyze")
async def analyze_data(db: Session = Depends(get_session)):
    """Run analysis on the dataset."""
    analysis_service.db = db
    return await analysis_service.run_analysis()


@api_router.get("/insights")
async def get_insights(db: Session = Depends(get_session)):
    """Get insights from the dataset."""
    analysis_service.db = db
    return await analysis_service.get_insights()
