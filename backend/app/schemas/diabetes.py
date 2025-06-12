from datetime import datetime
from typing import Optional

from app.models.diabetes import DataSource
from pydantic import BaseModel, Field


class DiabetesRecordBase(BaseModel):
    """Base schema for diabetes record data."""

    pregnancies: Optional[int] = Field(None, ge=0)
    glucose: int = Field(ge=0)
    blood_pressure: int = Field(ge=0)
    skin_thickness: int = Field(ge=0)
    insulin: int = Field(ge=0)
    bmi: float = Field(ge=0.0)
    diabetes_pedigree: float = Field(ge=0.0)
    age: int = Field(ge=0)
    outcome: Optional[bool] = None


class DiabetesRecordCreate(DiabetesRecordBase):
    """Schema for creating a new diabetes record."""

    user_id: int = Field(gt=0, description="ID of the user who owns this record")


class DiabetesRecordUpdate(BaseModel):
    """Schema for updating a diabetes record."""

    pregnancies: Optional[int] = Field(None, ge=0)
    glucose: Optional[int] = Field(None, ge=0)
    blood_pressure: Optional[int] = Field(None, ge=0)
    skin_thickness: Optional[int] = Field(None, ge=0)
    insulin: Optional[int] = Field(None, ge=0)
    bmi: Optional[float] = Field(None, ge=0.0)
    diabetes_pedigree: Optional[float] = Field(None, ge=0.0)
    age: Optional[int] = Field(None, ge=0)
    outcome: Optional[bool] = None


class DiabetesRecordInDB(DiabetesRecordBase):
    """Schema for diabetes record data as stored in the database."""

    id: int
    user_id: Optional[int] = None
    source: DataSource
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class DiabetesRecord(DiabetesRecordInDB):
    """Schema for diabetes record data returned to the client."""

    pass
