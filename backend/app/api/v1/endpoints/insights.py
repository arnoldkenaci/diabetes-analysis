from fastapi import APIRouter, Depends
from sqlalchemy import func, case, Integer
from sqlalchemy.orm import Session
from ....core.database import get_session
from ....models.diabetes import DiabetesRecord
from ....schemas.diabetes import InsightsResult

router = APIRouter()


@router.get("/", response_model=InsightsResult)
async def get_insights(db: Session = Depends(get_session)):
    """Get insights from the dataset."""
    # Age groups analysis
    age_groups = (
        db.query(
            func.floor(DiabetesRecord.age / 10) * 10,
            func.count(DiabetesRecord.id),
            func.avg(DiabetesRecord.outcome.cast(Integer)),
        )
        .group_by(func.floor(DiabetesRecord.age / 10))
        .all()
    )

    # BMI categories
    bmi_categories = (
        db.query(
            case(
                (DiabetesRecord.bmi < 18.5, "Underweight"),
                (DiabetesRecord.bmi < 25, "Normal"),
                (DiabetesRecord.bmi < 30, "Overweight"),
                else_="Obese",
            ),
            func.count(DiabetesRecord.id),
            func.avg(DiabetesRecord.outcome.cast(Integer)),
        )
        .group_by(
            case(
                (DiabetesRecord.bmi < 18.5, "Underweight"),
                (DiabetesRecord.bmi < 25, "Normal"),
                (DiabetesRecord.bmi < 30, "Overweight"),
                else_="Obese",
            )
        )
        .all()
    )

    return {
        "age_groups": [
            {
                "age_range": f"{age}-{age+9}",
                "count": count,
                "diabetes_rate": round(rate * 100, 2),
            }
            for age, count, rate in age_groups
        ],
        "bmi_categories": [
            {
                "category": category,
                "count": count,
                "diabetes_rate": round(rate * 100, 2),
            }
            for category, count, rate in bmi_categories
        ],
    }
