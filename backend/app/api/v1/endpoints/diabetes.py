from typing import Any

from app.core.database import get_session
from app.models.diabetes import DataSource, DiabetesRecord
from app.models.user import User
from app.schemas.diabetes import DiabetesRecord as DiabetesRecordSchema
from app.schemas.diabetes import DiabetesRecordCreate
from app.services.health import HealthService
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


async def assess_health_background(db: Session, user_id: int, record_id: int) -> None:
    """Background task to assess health after creating a diabetes record."""
    try:
        health_service = HealthService(db)
        await health_service.assess_health(user_id, record_id)
    except Exception as e:
        # Log the error but don't raise it since this is a background task
        print(f"Error in health assessment background task: {str(e)}")


@router.post("/", response_model=DiabetesRecordSchema)
async def create_diabetes_record(
    *,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
    record_in: DiabetesRecordCreate,
) -> Any:
    """
    Create new diabetes record for a user and start health assessment in background.
    """
    # Check if user exists
    user = db.query(User).filter(User.id == record_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    # Create new diabetes record
    record = DiabetesRecord(
        user_id=record_in.user_id,
        pregnancies=record_in.pregnancies,
        glucose=record_in.glucose,
        blood_pressure=record_in.blood_pressure,
        skin_thickness=record_in.skin_thickness,
        insulin=record_in.insulin,
        bmi=record_in.bmi,
        diabetes_pedigree=record_in.diabetes_pedigree,
        age=record_in.age,
        outcome=record_in.outcome,
        source=DataSource.USER_ENTRY,  # Always set as user_entry for API-created records
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Start health assessment in background
    background_tasks.add_task(
        assess_health_background,
        db=db,
        user_id=record_in.user_id,
        record_id=record.id,
    )

    return record
