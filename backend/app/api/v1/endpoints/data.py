from typing import Optional

from app.core.database import get_session
from app.core.scheduler import AnalysisScheduler
from app.services.data import DataService
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/")
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
    data_service = DataService(db)
    return data_service.get_records(
        min_age=min_age,
        max_age=max_age,
        min_bmi=min_bmi,
        max_bmi=max_bmi,
        min_glucose=min_glucose,
        max_glucose=max_glucose,
        outcome=outcome,
    )


@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_session),
):
    """Upload diabetes dataset and trigger background analysis."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    data_service = DataService(db)
    contents = await file.read()
    result = data_service.process_upload(contents, file.filename, user_id)

    # Trigger background analysis
    scheduler = AnalysisScheduler(db)
    await scheduler.run_background_analysis(user_id, result["attempt_id"])

    return result


@router.get("/attempts")
async def get_user_attempts(db: Session = Depends(get_session)):
    """Get history of user upload attempts."""
    data_service = DataService(db)
    return await data_service.get_user_attempts()


@router.get("/attempts/{attempt_id}/records")
async def get_attempt_records(attempt_id: str, db: Session = Depends(get_session)):
    """Get records for a specific upload attempt."""
    data_service = DataService(db)
    return data_service.get_attempt_records(attempt_id)
