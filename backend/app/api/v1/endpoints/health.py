from typing import Any

from app.core.database import get_session
from app.schemas.health import HealthAssessment as HealthAssessmentSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{assessment_id}", response_model=HealthAssessmentSchema)
def get_health_assessment(
    *,
    db: Session = Depends(get_session),
    assessment_id: int,
) -> Any:
    """
    Get a specific health assessment by ID.
    """
    from app.models.health import HealthAssessment

    assessment = (
        db.query(HealthAssessment).filter(HealthAssessment.id == assessment_id).first()
    )
    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Health assessment not found",
        )
    return assessment
