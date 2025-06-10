from datetime import datetime

from app.core.database import Base
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class HealthAssessment(Base):
    __tablename__ = "health_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diabetes_record_id = Column(
        Integer, ForeignKey("diabetes_records.id"), nullable=False
    )
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    recommendations = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="health_assessments")
    diabetes_record = relationship(
        "DiabetesRecord",
        back_populates="health_assessments",
        foreign_keys=[diabetes_record_id],
    )
    # Many-to-one relationship: a health assessment can be linked to multiple diabetes records
    diabetes_records = relationship(
        "DiabetesRecord",
        back_populates="health_assessment",
        foreign_keys="DiabetesRecord.health_assessment_id",
    )
