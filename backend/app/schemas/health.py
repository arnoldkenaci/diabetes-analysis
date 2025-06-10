from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class HealthAssessmentBase(BaseModel):
    risk_score: float = Field(..., description="Calculated risk score (0-1)")
    risk_level: str = Field(..., description="Risk level (low/medium/high)")
    recommendations: List[str] = Field(
        ..., description="List of health recommendations"
    )


class HealthAssessmentCreate(HealthAssessmentBase):
    user_id: int = Field(..., gt=0, description="ID of the user")
    diabetes_record_id: int = Field(..., gt=0, description="ID of the diabetes record")


class HealthAssessmentInDB(HealthAssessmentBase):
    id: int
    user_id: int
    diabetes_record_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class HealthAssessment(HealthAssessmentInDB):
    pass
