from sqlalchemy import (
    Integer,
    Float,
    Boolean,
    DateTime,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class DiabetesRecord(Base):  # type: ignore
    __tablename__ = "diabetes_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    pregnancies: Mapped[int] = mapped_column(Integer, nullable=False)
    glucose: Mapped[int] = mapped_column(Integer, nullable=False)
    blood_pressure: Mapped[int] = mapped_column(Integer, nullable=False)
    skin_thickness: Mapped[int] = mapped_column(Integer, nullable=False)
    insulin: Mapped[int] = mapped_column(Integer, nullable=False)
    bmi: Mapped[float] = mapped_column(Float, nullable=False)
    diabetes_pedigree: Mapped[float] = mapped_column(Float, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    outcome: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return (
            f"<DiabetesRecord(id={self.id}, age={self.age}, "
            f"glucose={self.glucose}, outcome={self.outcome})>"
        )
