from typing import Any, Dict

import pandas as pd
from app.core.config import get_settings
from app.models.diabetes import DataSource, DiabetesRecord
from app.models.health import HealthAssessment
from app.models.user import User
from app.services.llm import get_llm_recommendations
from app.services.notification import NotificationService
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy import inspect
from sqlalchemy.orm import Session

settings = get_settings()


class HealthService:
    """Service for health assessment and recommendations."""

    def __init__(self, db: Session):
        """Initialize the service."""
        self.db = db
        self.model = self._train_model()
        self.notification_service = NotificationService()

    def _train_model(self) -> RandomForestClassifier:
        """Train the risk assessment model using existing data."""
        # Get all dataset records
        records = (
            self.db.query(DiabetesRecord)
            .filter(DiabetesRecord.source == DataSource.DATASET)
            .all()
        )

        # Convert to DataFrame
        data = pd.DataFrame(
            [
                {
                    "pregnancies": r.pregnancies,
                    "glucose": r.glucose,
                    "blood_pressure": r.blood_pressure,
                    "skin_thickness": r.skin_thickness,
                    "insulin": r.insulin,
                    "bmi": r.bmi,
                    "diabetes_pedigree": r.diabetes_pedigree,
                    "age": r.age,
                    "outcome": r.outcome,
                }
                for r in records
            ]
        )

        # Prepare features and target
        X = data.drop("outcome", axis=1)
        y = data["outcome"]

        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        return model

    def _calculate_risk_score(self, record: DiabetesRecord) -> float:
        """Calculate risk score for a diabetes record."""
        # Create a list of feature values in the same order as training data
        features = pd.DataFrame(
            [
                [
                    record.pregnancies,
                    record.glucose,
                    record.blood_pressure,
                    record.skin_thickness,
                    record.insulin,
                    record.bmi,
                    record.diabetes_pedigree,
                    record.age,
                ]
            ],
            columns=[
                "pregnancies",
                "glucose",
                "blood_pressure",
                "skin_thickness",
                "insulin",
                "bmi",
                "diabetes_pedigree",
                "age",
            ],
        )
        return float(self.model.predict_proba(features)[0][1])

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on risk score."""
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.7:
            return "medium"
        return "high"

    def _generate_recommendations(
        self, record: DiabetesRecord, risk_level: str
    ) -> Dict[str, Any]:
        """Generate personalized health recommendations using LLM."""
        # Get recommendations using our existing LLM service
        recommendations = get_llm_recommendations(
            total_records=1,  # Single record assessment
            positive_cases=1 if risk_level == "high" else 0,
            positive_rate=100 if risk_level == "high" else 0,
            avg_glucose=float(record.glucose),
            avg_bmi=float(record.bmi),
            avg_age=float(record.age),
        )

        return {
            "risk_assessment": recommendations["risk_assessment"],
            "recommendations": recommendations["recommendations"],
            "preventive_measures": recommendations["preventive_measures"],
        }

    async def _send_notification(
        self, user: User, risk_level: str, recommendations: Dict[str, Any]
    ) -> None:
        """Send notification with assessment results and recommendations."""
        # Create dashboard URL
        dashboard_url = f"http://localhost:80/dashboard/{user.id}"

        # Prepare notification data
        notification_data = {
            "risk_level": risk_level.upper(),
            "risk_assessment": recommendations["risk_assessment"],
            "recommendations": recommendations["recommendations"],
            "preventive_measures": recommendations["preventive_measures"],
            "dashboard_url": dashboard_url,
        }

        # Send notification using our existing notification service
        await self.notification_service.send_notification(
            user_id=str(user.id),
            subject="Your Diabetes Risk Assessment Results",
            message=(
                "Your diabetes risk assessment has been completed. "
                f"Risk Level: {risk_level.upper()}"
            ),
            data=notification_data,
        )

    async def assess_health(self, user_id: int, record_id: int) -> HealthAssessment:
        """Assess health risk and create assessment record."""
        # Get user and record
        user = self.db.query(User).filter(User.id == user_id).first()
        record = (
            self.db.query(DiabetesRecord).filter(DiabetesRecord.id == record_id).first()
        )

        if not user or not record:
            raise ValueError("User or record not found")

        # Calculate risk score and level
        risk_score = self._calculate_risk_score(record)
        risk_level = self._determine_risk_level(risk_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(record, risk_level)

        # Create assessment record
        assessment = HealthAssessment(
            user_id=user_id,
            diabetes_record_id=record_id,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=recommendations,
        )
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        # Send notification
        await self._send_notification(user, risk_level, recommendations)

        return assessment
