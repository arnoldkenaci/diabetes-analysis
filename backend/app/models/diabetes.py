from sqlalchemy import Boolean, Column, DateTime, Float, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class DiabetesRecord(Base):
    """Diabetes record model."""

    __tablename__ = "diabetes_records"

    id = Column(Integer, primary_key=True, index=True)
    pregnancies = Column(Integer)
    glucose = Column(Integer)
    blood_pressure = Column(Integer)
    skin_thickness = Column(Integer)
    insulin = Column(Integer)
    bmi = Column(Float)
    diabetes_pedigree = Column(Float)
    age = Column(Integer)
    outcome = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=func.now(),
        onupdate=func.now(),
    )
