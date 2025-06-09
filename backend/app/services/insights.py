from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from app.models.diabetes import DiabetesRecord
from app.schemas.diabetes import AgeGroupAnalysis, BMICategoryAnalysis, InsightsResult
from app.services.base import BaseService
from sqlalchemy import func


class InsightsService(BaseService[DiabetesRecord]):
    """Service for generating insights from diabetes data analysis."""

    async def generate_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate insights from the analyzed data."""
        insights = {
            "summary": self._generate_summary(df),
            "trends": self._analyze_trends(df),
            "correlations": self._analyze_correlations(df),
            "risk_assessment": self._assess_risk(df),
        }
        return insights

    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a summary of the data."""
        return {
            "total_records": len(df),
            "average_values": {
                "glucose": round(df["glucose"].mean(), 2),
                "bmi": round(df["bmi"].mean(), 2),
                "age": round(df["age"].mean(), 2),
                "blood_pressure": round(df["blood_pressure"].mean(), 2),
            },
            "outcome_distribution": {
                "positive": int(df["outcome"].sum()),
                "negative": int(len(df) - df["outcome"].sum()),
            },
        }

    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in the data."""
        trends = {}

        # Analyze glucose trends
        if len(df) > 1:
            glucose_trend = np.polyfit(range(len(df)), df["glucose"], 1)[0]
            trends["glucose"] = {
                "direction": "increasing" if glucose_trend > 0 else "decreasing",
                "rate": round(abs(glucose_trend), 2),
            }

        # Analyze BMI trends
        if len(df) > 1:
            bmi_trend = np.polyfit(range(len(df)), df["bmi"], 1)[0]
            trends["bmi"] = {
                "direction": "increasing" if bmi_trend > 0 else "decreasing",
                "rate": round(abs(bmi_trend), 2),
            }

        return trends

    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between variables."""
        correlations = {}

        # Calculate correlations with outcome
        for column in df.columns:
            if column != "outcome":
                corr = df[column].corr(df["outcome"])
                correlations[column] = {
                    "correlation": round(corr, 2),
                    "strength": self._get_correlation_strength(corr),
                }

        return correlations

    def _assess_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall risk based on the data."""
        risk_factors = []

        # Check glucose levels
        if df["glucose"].mean() > 140:
            risk_factors.append(
                {
                    "factor": "High Average Glucose",
                    "value": round(df["glucose"].mean(), 2),
                    "threshold": 140,
                    "severity": "high",
                }
            )

        # Check BMI
        if df["bmi"].mean() > 30:
            risk_factors.append(
                {
                    "factor": "High BMI",
                    "value": round(df["bmi"].mean(), 2),
                    "threshold": 30,
                    "severity": "high",
                }
            )

        # Check age
        if df["age"].mean() > 45:
            risk_factors.append(
                {
                    "factor": "Age",
                    "value": round(df["age"].mean(), 2),
                    "threshold": 45,
                    "severity": "medium",
                }
            )

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(df)

        return {
            "risk_factors": risk_factors,
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
        }

    def _get_correlation_strength(self, correlation: float) -> str:
        """Get the strength of correlation based on the correlation coefficient."""
        abs_corr = abs(correlation)
        if abs_corr >= 0.7:
            return "strong"
        elif abs_corr >= 0.5:
            return "moderate"
        elif abs_corr >= 0.3:
            return "weak"
        else:
            return "very weak"

    def _calculate_risk_score(self, df: pd.DataFrame) -> float:
        """Calculate an overall risk score based on various factors."""
        score = 0.0

        # Glucose contribution
        glucose_mean = df["glucose"].mean()
        if glucose_mean > 140:
            score += 0.4
        elif glucose_mean > 100:
            score += 0.2

        # BMI contribution
        bmi_mean = df["bmi"].mean()
        if bmi_mean > 30:
            score += 0.3
        elif bmi_mean > 25:
            score += 0.15

        # Age contribution
        age_mean = df["age"].mean()
        if age_mean > 45:
            score += 0.3
        elif age_mean > 35:
            score += 0.15

        return round(score, 2)

    def _get_risk_level(self, risk_score: float) -> str:
        """Get the risk level based on the risk score."""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    def get_insights(self) -> InsightsResult:
        """Generate insights from diabetes records."""
        with self.get_session() as db:
            # Get total records
            total_records = db.query(func.count(DiabetesRecord.id)).scalar()
            if total_records == 0:
                return InsightsResult(
                    total_records=0,
                    age_groups=[],
                    bmi_categories=[],
                    average_glucose=None,
                    diabetes_rate=None,
                    age_risk=None,
                    bmi_risk=None,
                )

            # Calculate age group analysis
            age_groups = self._analyze_age_groups(db)

            # Calculate BMI category analysis
            bmi_categories = self._analyze_bmi_categories(db)

            # Calculate overall statistics
            avg_glucose = db.query(func.avg(DiabetesRecord.glucose)).scalar()
            diabetes_rate = (
                db.query(func.count(DiabetesRecord.id))
                .filter(DiabetesRecord.diabetes == True)
                .scalar()
                / total_records
            ) * 100

            # Calculate risk factors
            age_risk = self._calculate_age_risk(db)
            bmi_risk = self._calculate_bmi_risk(db)

            return InsightsResult(
                total_records=total_records,
                age_groups=age_groups,
                bmi_categories=bmi_categories,
                average_glucose=round(avg_glucose, 2) if avg_glucose else None,
                diabetes_rate=round(diabetes_rate, 2),
                age_risk=age_risk,
                bmi_risk=bmi_risk,
            )

    def _analyze_age_groups(self, db) -> List[AgeGroupAnalysis]:
        """Analyze diabetes rates by age groups."""
        age_groups = []
        age_ranges = [
            (0, 20, "0-20"),
            (21, 40, "21-40"),
            (41, 60, "41-60"),
            (61, 80, "61-80"),
            (81, 100, "81-100"),
        ]

        for min_age, max_age, label in age_ranges:
            total = (
                db.query(func.count(DiabetesRecord.id))
                .filter(DiabetesRecord.age >= min_age, DiabetesRecord.age <= max_age)
                .scalar()
            )

            if total > 0:
                diabetic = (
                    db.query(func.count(DiabetesRecord.id))
                    .filter(
                        DiabetesRecord.age >= min_age,
                        DiabetesRecord.age <= max_age,
                        DiabetesRecord.diabetes == True,
                    )
                    .scalar()
                )

                rate = (diabetic / total) * 100
                age_groups.append(
                    AgeGroupAnalysis(
                        age_range=label,
                        count=total,
                        diabetic_count=diabetic,
                        diabetes_rate=round(rate, 2),
                    )
                )

        return age_groups

    def _analyze_bmi_categories(self, db) -> List[BMICategoryAnalysis]:
        """Analyze diabetes rates by BMI categories."""
        bmi_categories = []
        bmi_ranges = [
            (0, 18.5, "Underweight"),
            (18.5, 25, "Normal"),
            (25, 30, "Overweight"),
            (30, 35, "Obese Class I"),
            (35, 40, "Obese Class II"),
            (40, 100, "Obese Class III"),
        ]

        for min_bmi, max_bmi, label in bmi_ranges:
            total = (
                db.query(func.count(DiabetesRecord.id))
                .filter(DiabetesRecord.bmi >= min_bmi, DiabetesRecord.bmi < max_bmi)
                .scalar()
            )

            if total > 0:
                diabetic = (
                    db.query(func.count(DiabetesRecord.id))
                    .filter(
                        DiabetesRecord.bmi >= min_bmi,
                        DiabetesRecord.bmi < max_bmi,
                        DiabetesRecord.diabetes == True,
                    )
                    .scalar()
                )

                rate = (diabetic / total) * 100
                bmi_categories.append(
                    BMICategoryAnalysis(
                        category=label,
                        count=total,
                        diabetic_count=diabetic,
                        diabetes_rate=round(rate, 2),
                    )
                )

        return bmi_categories

    def _calculate_age_risk(self, db) -> Optional[Dict[str, float]]:
        """Calculate age-related risk factors."""
        # Calculate average glucose levels by age
        age_glucose = (
            db.query(
                DiabetesRecord.age,
                func.avg(DiabetesRecord.glucose).label("avg_glucose"),
            )
            .group_by(DiabetesRecord.age)
            .all()
        )

        if not age_glucose:
            return None

        # Calculate correlation between age and glucose
        ages = [r[0] for r in age_glucose]
        glucose_levels = [r[1] for r in age_glucose]

        correlation = self._calculate_correlation(ages, glucose_levels)

        return {"correlation": round(correlation, 2)}

    def _calculate_bmi_risk(self, db) -> Optional[Dict[str, float]]:
        """Calculate BMI-related risk factors."""
        # Calculate average glucose levels by BMI
        bmi_glucose = (
            db.query(
                DiabetesRecord.bmi,
                func.avg(DiabetesRecord.glucose).label("avg_glucose"),
            )
            .group_by(DiabetesRecord.bmi)
            .all()
        )

        if not bmi_glucose:
            return None

        # Calculate correlation between BMI and glucose
        bmis = [r[0] for r in bmi_glucose]
        glucose_levels = [r[1] for r in bmi_glucose]

        correlation = self._calculate_correlation(bmis, glucose_levels)

        return {"correlation": round(correlation, 2)}

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient between two lists."""
        n = len(x)
        if n != len(y) or n == 0:
            return 0.0

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = (
            (n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)
        ) ** 0.5

        if denominator == 0:
            return 0.0

        return numerator / denominator
