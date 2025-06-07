from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ....core.database import get_session
from ....models.diabetes import DiabetesRecord
from ....schemas.diabetes import AnalysisResult
from ....services.llm import get_llm_recommendations

router = APIRouter()


@router.get("/", response_model=AnalysisResult)
async def analyze_data(db: Session = Depends(get_session)):
    """Run basic analysis on the dataset."""
    # Get basic statistics
    total_records = db.query(DiabetesRecord).count()
    positive_cases = (
        db.query(DiabetesRecord).filter(DiabetesRecord.outcome.is_(True)).count()
    )

    # Calculate average values
    avg_glucose = db.query(func.avg(DiabetesRecord.glucose)).scalar()
    avg_bmi = db.query(func.avg(DiabetesRecord.bmi)).scalar()
    avg_age = db.query(func.avg(DiabetesRecord.age)).scalar()

    # Calculate positive rate
    positive_rate = (positive_cases / total_records) * 100 if total_records > 0 else 0

    # Get LLM recommendations based on the analysis
    recommendations = await get_llm_recommendations(
        total_records=total_records,
        positive_cases=positive_cases,
        positive_rate=positive_rate,
        avg_glucose=avg_glucose,
        avg_bmi=avg_bmi,
        avg_age=avg_age,
    )

    return {
        "total_records": total_records,
        "positive_cases": positive_cases,
        "positive_rate": positive_rate,
        "average_glucose": round(avg_glucose, 2) if avg_glucose else 0,
        "average_bmi": round(avg_bmi, 2) if avg_bmi else 0,
        "average_age": round(avg_age, 2) if avg_age else 0,
        "recommendations": recommendations.get("recommendations", []),
        "risk_assessment": recommendations.get("risk_assessment", ""),
        "preventive_measures": recommendations.get("preventive_measures", []),
    }
