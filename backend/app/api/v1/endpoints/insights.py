from fastapi import APIRouter, Depends
from sqlalchemy import func, case, Integer
from sqlalchemy.orm import Session
from typing import Optional
from ....core.database import get_session
from ....models.diabetes import DiabetesRecord
from ....schemas.diabetes import InsightsResult

router = APIRouter()


def _analyze_age_risk(db: Session) -> Optional[str]:
    """Analyze age-based risk factors."""
    records = db.query(DiabetesRecord).all()
    age_groups = {
        "0-30": (0, 30),
        "31-50": (31, 50),
        "51-70": (51, 70),
        "70+": (71, float("inf")),
    }

    for group, (min_age, max_age) in age_groups.items():
        group_records = [r for r in records if min_age <= r.age <= max_age]
        if not group_records:
            continue

        diabetes_rate = sum(1 for r in group_records if r.outcome) / len(group_records)
        if diabetes_rate > 0.5:
            return f"High risk in age group {group}"

    return None


def _analyze_bmi_risk(db: Session) -> Optional[str]:
    """Analyze BMI-based risk factors."""
    records = db.query(DiabetesRecord).all()
    bmi_categories = {
        "Underweight": (0, 18.5),
        "Normal": (18.5, 25),
        "Overweight": (25, 30),
        "Obese": (30, float("inf")),
    }

    for category, (min_bmi, max_bmi) in bmi_categories.items():
        category_records = [r for r in records if min_bmi <= r.bmi < max_bmi]
        if not category_records:
            continue

        diabetes_rate = sum(1 for r in category_records if r.outcome) / len(
            category_records
        )
        if diabetes_rate > 0.4:
            return f"High risk in {category} category"

    return None


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

    # Calculate risk assessments
    age_risk_assessment = _analyze_age_risk(db)
    bmi_risk_assessment = _analyze_bmi_risk(db)

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
        "age_risk": age_risk_assessment,
        "bmi_risk": bmi_risk_assessment,
    }
