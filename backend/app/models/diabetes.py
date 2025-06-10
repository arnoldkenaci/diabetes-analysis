import enum

from app.core.database import Base
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class DataSource(str, enum.Enum):
    """Source of the diabetes record data."""

    DATASET = "dataset"
    USER_ENTRY = "user_entry"


class DiabetesRecord(Base):
    """Model for diabetes records."""

    __tablename__ = "diabetes_records"

    id = Column(Integer, primary_key=True, nullable=False)

    # Health Data
    pregnancies = Column(Integer, nullable=False)
    glucose = Column(Integer, nullable=False)
    blood_pressure = Column(Integer, nullable=False)
    skin_thickness = Column(Integer, nullable=False)
    insulin = Column(Integer, nullable=False)
    bmi = Column(Float, nullable=False)
    diabetes_pedigree = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    outcome = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the person has diabetes (1 = yes, 0 = no)",
    )

    # Record source from user entry/dataset
    source = Column(Enum(DataSource), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="diabetes_records")

    health_assessment_id = Column(
        Integer, ForeignKey("health_assessments.id"), nullable=True
    )
    health_assessment = relationship(
        "HealthAssessment",
        back_populates="diabetes_records",
        foreign_keys=[health_assessment_id],
    )
    # One-to-many relationship: a diabetes record can have multiple health assessments
    health_assessments = relationship(
        "HealthAssessment",
        back_populates="diabetes_record",
        foreign_keys="HealthAssessment.diabetes_record_id",
    )
