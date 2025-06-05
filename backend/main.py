from fastapi import FastAPI, Query, Depends
from sqlalchemy import func, case, Integer
from sqlalchemy.orm import Session
from models import DiabetesRecord
from typing import Optional, Annotated
from fastapi.middleware.cors import CORSMiddleware
from database import get_session

# Create FastAPI app
app = FastAPI(
    title="Diabetes Dataset Analysis API",
    description="API for analyzing diabetes dataset and providing insights",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a reusable database dependency
DB = Annotated[Session, Depends(get_session)]


@app.get("/")
async def root():
    return {"message": "Welcome to Diabetes Dataset Analysis API"}


@app.get("/data")
async def get_data(
    db: DB,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    outcome: Optional[bool] = None,
):
    """Get diabetes records with optional filters"""
    query = db.query(DiabetesRecord)

    if min_age is not None:
        query = query.filter(DiabetesRecord.age >= min_age)
    if max_age is not None:
        query = query.filter(DiabetesRecord.age <= max_age)
    if outcome is not None:
        query = query.filter(DiabetesRecord.outcome == outcome)

    total = query.count()
    records = query.offset(offset).limit(limit).all()

    return {"total": total, "offset": offset, "limit": limit, "data": records}


@app.get("/analyze")
async def analyze_data(db: DB):
    """Run basic analysis on the dataset"""
    # Get basic statistics
    total_records = db.query(DiabetesRecord).count()
    positive_cases = (
        db.query(DiabetesRecord).filter(DiabetesRecord.outcome.is_(True)).count()
    )

    # Calculate average values
    avg_glucose = db.query(func.avg(DiabetesRecord.glucose)).scalar()
    avg_bmi = db.query(func.avg(DiabetesRecord.bmi)).scalar()
    avg_age = db.query(func.avg(DiabetesRecord.age)).scalar()

    return {
        "total_records": total_records,
        "positive_cases": positive_cases,
        "positive_rate": (
            (positive_cases / total_records) * 100 if total_records > 0 else 0
        ),
        "average_glucose": round(avg_glucose, 2) if avg_glucose else 0,
        "average_bmi": round(avg_bmi, 2) if avg_bmi else 0,
        "average_age": round(avg_age, 2) if avg_age else 0,
    }


@app.get("/insights")
async def get_insights(db: DB):
    """Get insights from the dataset"""
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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
