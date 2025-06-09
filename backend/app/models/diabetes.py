import enum
from datetime import datetime

from app.core.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class DataSource(str, enum.Enum):
    DATASET = "dataset"
    USER_UPLOAD = "user_upload"


class UserAttempt(Base):
    """Model for user upload attempts."""

    __tablename__ = "user_attempts"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    records_count = Column(Integer, default=0)
    status = Column(String, nullable=False)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    records = relationship("DiabetesRecord", back_populates="user_attempt")


class DiabetesRecord(Base):
    """Model for diabetes records."""

    __tablename__ = "diabetes_records"

    id = Column(String, primary_key=True)
    pregnancies = Column(Integer, nullable=False)
    glucose = Column(Integer, nullable=False)
    blood_pressure = Column(Integer, nullable=False)
    skin_thickness = Column(Integer, nullable=False)
    insulin = Column(Integer, nullable=False)
    bmi = Column(Float, nullable=False)
    diabetes_pedigree = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    source = Column(Enum(DataSource), nullable=False)
    user_attempt_id = Column(String, ForeignKey("user_attempts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_attempt = relationship("UserAttempt", back_populates="records")
