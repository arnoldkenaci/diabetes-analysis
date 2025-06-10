from typing import Any

from app.core.database import get_session
from app.schemas.health import HealthAssessment as HealthAssessmentSchema
from app.services.health import HealthService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/assess/{user_id}/{record_id}", response_model=HealthAssessmentSchema)
def assess_health(
    *,
    db: Session = Depends(get_session),
    user_id: int,
    record_id: int,
) -> Any:
    """
    Assess health risk for a user's diabetes record.
    """
    try:
        health_service = HealthService(db)
        assessment = health_service.assess_health(user_id, record_id)
        return assessment
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during health assessment: {str(e)}",
        )
