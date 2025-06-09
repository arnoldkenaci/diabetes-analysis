from datetime import datetime
from typing import List, Optional

from app.models.diabetes import DataSource
from pydantic import BaseModel, ConfigDict, Field


class DiabetesRecordBase(BaseModel):
    """Base diabetes record schema."""

    model_config = ConfigDict(from_attributes=True)

    pregnancies: int = Field(..., ge=0, le=20)
    glucose: int = Field(..., ge=0, le=300)
    blood_pressure: int = Field(..., ge=0, le=150)
    skin_thickness: int = Field(..., ge=0, le=100)
    insulin: int = Field(..., ge=0, le=1000)
    bmi: float = Field(..., ge=0, le=100)
    diabetes_pedigree: float = Field(..., ge=0, le=3)
    age: int = Field(..., ge=0, le=120)
    source: DataSource


class DiabetesRecordCreate(DiabetesRecordBase):
    """Schema for creating a diabetes record."""

    pass


class DiabetesRecord(DiabetesRecordBase):
    """Schema for diabetes record with ID and timestamps."""

    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class DiabetesRecordList(BaseModel):
    """Schema for list of diabetes records."""

    model_config = ConfigDict(from_attributes=True)

    total: int
    offset: int
    limit: int
    data: list[DiabetesRecord]


class AnalysisResult(BaseModel):
    """Schema for analysis results."""

    model_config = ConfigDict(from_attributes=True)

    total_records: int
    positive_cases: int
    positive_rate: float
    average_glucose: float
    average_bmi: float
    average_age: float
    recommendations: Optional[List[str]] = None
    risk_assessment: Optional[str] = None
    preventive_measures: Optional[List[str]] = None


class AgeGroupAnalysis(BaseModel):
    age_range: str
    count: int
    diabetes_rate: float


class BMICategoryAnalysis(BaseModel):
    category: str
    count: int
    diabetes_rate: float


class InsightsResult(BaseModel):
    """Schema for insights results."""

    age_groups: List[AgeGroupAnalysis]
    bmi_categories: List[BMICategoryAnalysis]
    age_risk: Optional[str] = None
    bmi_risk: Optional[str] = None
