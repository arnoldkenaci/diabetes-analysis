from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DiabetesRecordBase(BaseModel):
    """Base diabetes record schema."""

    pregnancies: int
    glucose: int
    blood_pressure: int
    skin_thickness: int
    insulin: int
    bmi: float
    diabetes_pedigree: float
    age: int
    outcome: bool


class DiabetesRecordCreate(DiabetesRecordBase):
    """Schema for creating a diabetes record."""

    pass


class DiabetesRecord(DiabetesRecordBase):
    """Schema for diabetes record response."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DiabetesRecordList(BaseModel):
    """Schema for list of diabetes records."""

    total: int
    offset: int
    limit: int
    data: list[DiabetesRecord]


class AnalysisResult(BaseModel):
    """Schema for analysis results."""

    total_records: int
    positive_cases: int
    positive_rate: float
    average_glucose: float
    average_bmi: float
    average_age: float


class AgeGroup(BaseModel):
    """Schema for age group analysis."""

    age_range: str
    count: int
    diabetes_rate: float


class BMICategory(BaseModel):
    """Schema for BMI category analysis."""

    category: str
    count: int
    diabetes_rate: float


class InsightsResult(BaseModel):
    """Schema for insights results."""

    age_groups: list[AgeGroup]
    bmi_categories: list[BMICategory]
