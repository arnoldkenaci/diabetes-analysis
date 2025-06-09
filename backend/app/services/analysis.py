import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from app.core.config import get_settings
from app.models.diabetes import DiabetesRecord, UserAttempt
from app.services.base import BaseService
from app.services.insights import InsightsService
from app.services.llm import LLMService
from app.services.notification import NotificationService
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sqlalchemy import Integer, case, func
from sqlalchemy.orm import Session

settings = get_settings()


class AnalysisService(BaseService[UserAttempt]):
    """Service for analyzing diabetes dataset."""

    def __init__(
        self,
        insights_service: InsightsService,
        notification_service: NotificationService,
        db: Session,
    ):
        super().__init__(db=db)
        self.insights_service = insights_service
        self.notification_service = notification_service
        self.llm_service = LLMService()
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()

    async def get_filtered_data(
        self,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        min_bmi: Optional[float] = None,
        max_bmi: Optional[float] = None,
        min_glucose: Optional[float] = None,
        max_glucose: Optional[float] = None,
        outcome: Optional[bool] = None,
    ) -> List[DiabetesRecord]:
        """Get filtered diabetes data."""
        with self.get_session() as db:
            query = db.query(DiabetesRecord)

            if min_age is not None:
                query = query.filter(DiabetesRecord.age >= min_age)
            if max_age is not None:
                query = query.filter(DiabetesRecord.age <= max_age)
            if min_bmi is not None:
                query = query.filter(DiabetesRecord.bmi >= min_bmi)
            if max_bmi is not None:
                query = query.filter(DiabetesRecord.bmi <= max_bmi)
            if min_glucose is not None:
                query = query.filter(DiabetesRecord.glucose >= min_glucose)
            if max_glucose is not None:
                query = query.filter(DiabetesRecord.glucose <= max_glucose)
            if outcome is not None:
                query = query.filter(DiabetesRecord.outcome == outcome)

            return query.all()

    async def run_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis on the dataset."""
        with self.get_session() as db:
            # Create analysis attempt record
            attempt_id = str(uuid.uuid4())
            attempt = UserAttempt(
                id=attempt_id, filename="analysis", records_count=0, status="processing"
            )
            db.add(attempt)
            db.commit()

            try:
                # Get all analysis results
                anomalies = self.detect_anomalies()
                kpis = self.calculate_kpis()
                trends = self.analyze_trends()

                # Get LLM recommendations
                recommendations = self.llm_service.get_analysis_recommendations(
                    self.llm_service._make_hashable(
                        {
                            "total_records": kpis["total_records"],
                            "positive_cases": kpis["positive_cases"],
                            "positive_rate": kpis["positive_rate"],
                            "avg_glucose": kpis["average_glucose"],
                            "avg_bmi": kpis["average_bmi"],
                            "avg_age": kpis["average_age"],
                        }
                    )
                )

                # Extract the risk assessment from the summary field
                risk_assessment = recommendations.get("risk_assessment", "")
                if not risk_assessment and "summary" in recommendations:
                    risk_assessment = recommendations["summary"]

                # Update attempt status
                attempt.status = "success"
                attempt.records_count = kpis["total_records"]
                attempt.completed_at = datetime.utcnow()
                db.commit()

                # Prepare notification message
                notification_message = {
                    "insights": {
                        "risk_factors": {
                            "high_glucose": kpis["high_glucose_rate"] > 30,
                            "obesity": kpis["obesity_rate"] > 25,
                        },
                        "age_risk": self._analyze_age_risk(),
                        "bmi_risk": self._analyze_bmi_risk(),
                    },
                    "recommendations": recommendations.get("recommendations", []),
                    "timestamp": datetime.utcnow().isoformat(),
                }

                # Send notification
                await self.notification_service.send_notification(
                    user_id=attempt.user_id,
                    message=self._format_insights_message(notification_message),
                    notification_type="analysis_complete",
                )

                return {
                    "total_records": kpis["total_records"],
                    "positive_cases": kpis["positive_cases"],
                    "positive_rate": kpis["positive_rate"],
                    "average_glucose": kpis["average_glucose"],
                    "average_bmi": kpis["average_bmi"],
                    "average_age": kpis["average_age"],
                    "anomalies": anomalies,
                    "metrics": kpis,
                    "trends": trends,
                    "recommendations": recommendations.get("recommendations", []),
                    "risk_assessment": risk_assessment,
                    "preventive_measures": recommendations.get(
                        "preventive_measures", []
                    ),
                }

            except Exception as e:
                # Update attempt status
                attempt.status = "failed"
                attempt.error_message = str(e)
                attempt.completed_at = datetime.utcnow()
                db.commit()

                # Send failure notification
                await self.notification_service.send_notification(
                    message=f"Analysis failed: {str(e)}",
                    notification_type="analysis_failed",
                )
                raise e

    def detect_anomalies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detect anomalies in the dataset using IQR method."""
        with self.get_session() as db:
            records = db.query(DiabetesRecord).all()

            # Convert to numpy arrays for analysis
            data = {
                "glucose": np.array([r.glucose for r in records]),
                "bmi": np.array([r.bmi for r in records]),
                "age": np.array([r.age for r in records]),
            }

            anomalies = {}
            for field, values in data.items():
                # Calculate IQR
                q1 = np.percentile(values, 25)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1

                # Define bounds
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                # Find anomalies
                condition = (values < lower_bound) | (values > upper_bound)
                anomaly_indices = np.where(condition)[0]

                anomalies[field] = [
                    {
                        "value": float(values[i]),
                        "record_id": records[i].id,
                        "deviation": float(values[i] - np.mean(values)),
                    }
                    for i in anomaly_indices
                ]

            return anomalies

    def calculate_kpis(self) -> Dict[str, float]:
        """Calculate key performance indicators."""
        with self.get_session() as db:
            # Get total records
            total_records = db.query(DiabetesRecord).count()

            # Calculate positive cases
            positive_cases = (
                db.query(DiabetesRecord)
                .filter(DiabetesRecord.diabetes.is_(True))
                .count()
            )

            # Calculate average values
            avg_glucose = db.query(func.avg(DiabetesRecord.glucose)).scalar()
            avg_bmi = db.query(func.avg(DiabetesRecord.bmi)).scalar()
            avg_age = db.query(func.avg(DiabetesRecord.age)).scalar()

            # Calculate risk factors
            high_glucose = (
                db.query(DiabetesRecord).filter(DiabetesRecord.glucose > 140).count()
            )

            high_bmi = db.query(DiabetesRecord).filter(DiabetesRecord.bmi > 30).count()

            # Calculate rates
            positive_rate = (
                (positive_cases / total_records) * 100 if total_records > 0 else 0
            )
            high_glucose_rate = (
                (high_glucose / total_records) * 100 if total_records > 0 else 0
            )
            obesity_rate = (high_bmi / total_records) * 100 if total_records > 0 else 0

            return {
                "total_records": total_records,
                "positive_cases": positive_cases,
                "positive_rate": positive_rate,
                "average_glucose": round(avg_glucose, 2) if avg_glucose else 0,
                "average_bmi": round(avg_bmi, 2) if avg_bmi else 0,
                "average_age": round(avg_age, 2) if avg_age else 0,
                "high_glucose_rate": high_glucose_rate,
                "obesity_rate": obesity_rate,
            }

    def analyze_trends(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze trends in the dataset."""
        with self.get_session() as db:
            # Age group analysis
            age_groups = (
                db.query(
                    func.floor(DiabetesRecord.age / 10) * 10,
                    func.count(DiabetesRecord.id),
                    func.avg(DiabetesRecord.diabetes.cast(Integer)),
                )
                .group_by(func.floor(DiabetesRecord.age / 10))
                .all()
            )

            # BMI category analysis
            bmi_case = case(
                {
                    DiabetesRecord.bmi < 18.5: "Underweight",
                    DiabetesRecord.bmi < 25: "Normal",
                    DiabetesRecord.bmi < 30: "Overweight",
                },
                else_="Obese",
            )

            bmi_categories = (
                db.query(
                    bmi_case.label("category"),
                    func.count(DiabetesRecord.id),
                    func.avg(DiabetesRecord.diabetes.cast(Integer)),
                )
                .group_by(bmi_case)
                .all()
            )

            return {
                "age_trends": [
                    {
                        "age_range": f"{age}-{age+9}",
                        "count": count,
                        "diabetes_rate": round(rate * 100, 2),
                    }
                    for age, count, rate in age_groups
                ],
                "bmi_trends": [
                    {
                        "category": category,
                        "count": count,
                        "diabetes_rate": round(rate * 100, 2),
                    }
                    for category, count, rate in bmi_categories
                ],
            }

    def _analyze_age_risk(self) -> Optional[str]:
        """Analyze age-based risk factors."""
        with self.get_session() as db:
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

                diabetes_rate = sum(1 for r in group_records if r.diabetes) / len(
                    group_records
                )
                if diabetes_rate > 0.5:
                    return f"High risk in age group {group}"

            return None

    def _analyze_bmi_risk(self) -> Optional[str]:
        """Analyze BMI-based risk factors."""
        with self.get_session() as db:
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

                diabetes_rate = sum(1 for r in category_records if r.diabetes) / len(
                    category_records
                )
                if diabetes_rate > 0.4:
                    return f"High risk in {category} category"

            return None

    async def get_insights(self) -> Dict[str, Any]:
        """Get insights from the dataset."""
        with self.get_session() as db:
            kpis = self.calculate_kpis()
            age_risk = self._analyze_age_risk()
            bmi_risk = self._analyze_bmi_risk()

            insights = {
                "risk_factors": {
                    "high_glucose": kpis["high_glucose_rate"] > 30,
                    "obesity": kpis["obesity_rate"] > 25,
                },
                "age_risk": age_risk,
                "bmi_risk": bmi_risk,
            }

            return {
                "insights": insights,
                "recommendations": [],  # Will be generated by LLM
            }

    def analyze_data(self, attempt_id: str) -> Dict[str, Any]:
        """Analyze diabetes data and send notifications."""
        with self.get_session() as db:
            # Get the user attempt
            attempt = db.query(UserAttempt).filter(UserAttempt.id == attempt_id).first()
            if not attempt:
                raise ValueError(f"Attempt {attempt_id} not found")

            try:
                # Get insights
                insights = self.insights_service.get_insights()

                # Update attempt status
                attempt.status = "completed"
                db.commit()

                # Prepare notification message
                message = self._format_insights_message(insights)

                # Send notification
                self.notification_service.send_notification(
                    user_id=attempt.user_id,
                    message=message,
                    notification_type="analysis_complete",
                )

                return {
                    "status": "success",
                    "message": "Analysis completed successfully",
                    "insights": insights,
                }

            except Exception as e:
                # Update attempt status
                attempt.status = "failed"
                attempt.error_message = str(e)
                db.commit()

                # Send error notification
                self.notification_service.send_notification(
                    user_id=attempt.user_id,
                    message=f"Analysis failed: {str(e)}",
                    notification_type="analysis_failed",
                )

                raise

    def _format_insights_message(self, insights: Any) -> str:
        """Format insights into a readable message."""
        message = ["Diabetes Analysis Results:"]

        # Add overall statistics
        message.append(f"\nTotal Records: {insights.total_records}")
        if insights.average_glucose:
            message.append(f"Average Glucose: {insights.average_glucose}")
        if insights.diabetes_rate:
            message.append(f"Diabetes Rate: {insights.diabetes_rate}%")

        # Add age group analysis
        if insights.age_groups:
            message.append("\nAge Group Analysis:")
            for group in insights.age_groups:
                message.append(
                    f"- {group.age_range}: {group.diabetes_rate}% diabetes rate "
                    f"({group.diabetic_count}/{group.count} records)"
                )

        # Add BMI category analysis
        if insights.bmi_categories:
            message.append("\nBMI Category Analysis:")
            for category in insights.bmi_categories:
                message.append(
                    f"- {category.category}: {category.diabetes_rate}% diabetes rate "
                    f"({category.diabetic_count}/{category.count} records)"
                )

        # Add risk factors
        if insights.age_risk:
            message.append(
                f"\nAge Risk Correlation: {insights.age_risk['correlation']}"
            )
        if insights.bmi_risk:
            message.append(f"BMI Risk Correlation: {insights.bmi_risk['correlation']}")

        return "\n".join(message)

    async def analyze_user_data(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's diabetes data and generate insights."""
        with self.get_session() as db:
            # Get user's data
            records = (
                db.query(DiabetesRecord)
                .join(UserAttempt)
                .filter(UserAttempt.user_id == user_id)
                .all()
            )

            if not records:
                return {
                    "status": "no_data",
                    "message": "No data available for analysis",
                }

            # Convert to DataFrame
            df = pd.DataFrame(
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

            # Prepare features
            X = df.drop("outcome", axis=1)
            y = df["outcome"]

            # Scale features
            X_scaled = self.scaler.fit_transform(X)

            # Train model
            self.model.fit(X_scaled, y)

            # Get feature importance
            feature_importance = dict(zip(X.columns, self.model.feature_importances_))

            # Generate insights
            insights = await self.insights_service.generate_insights(df)

            # Prepare analysis results
            results = {
                "status": "success",
                "data_points": len(records),
                "feature_importance": feature_importance,
                "insights": insights,
                "risk_factors": self._identify_risk_factors(df),
                "recommendations": self._generate_recommendations(df, insights),
                "charts": self._prepare_chart_data(df),
            }

            # Send notification
            await self.notification_service.send_notification(
                user_id=user_id,
                subject="Your Diabetes Analysis Results",
                message=self._format_notification_message(results),
                data=results,
            )

            return results

    def _identify_risk_factors(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify potential risk factors from the data."""
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

        return risk_factors

    def _generate_recommendations(
        self, df: pd.DataFrame, insights: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized recommendations based on the analysis."""
        recommendations = []

        # Add recommendations based on risk factors
        if df["glucose"].mean() > 140:
            recommendations.append("Consider regular blood glucose monitoring")
            recommendations.append(
                "Consult with a healthcare provider about glucose management"
            )

        if df["bmi"].mean() > 30:
            recommendations.append("Consider lifestyle changes to manage weight")
            recommendations.append("Consult with a nutritionist for dietary advice")

        # Add general recommendations
        recommendations.append("Maintain regular physical activity")
        recommendations.append(
            "Schedule regular check-ups with your healthcare provider"
        )

        return recommendations

    def _prepare_chart_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for visualization charts."""
        return {
            "glucose_trend": {
                "labels": list(range(len(df))),
                "values": df["glucose"].tolist(),
            },
            "bmi_distribution": {
                "labels": ["Underweight", "Normal", "Overweight", "Obese"],
                "values": [
                    len(df[df["bmi"] < 18.5]),
                    len(df[(df["bmi"] >= 18.5) & (df["bmi"] < 25)]),
                    len(df[(df["bmi"] >= 25) & (df["bmi"] < 30)]),
                    len(df[df["bmi"] >= 30]),
                ],
            },
            "age_distribution": {
                "labels": ["<30", "30-40", "40-50", "50-60", ">60"],
                "values": [
                    len(df[df["age"] < 30]),
                    len(df[(df["age"] >= 30) & (df["age"] < 40)]),
                    len(df[(df["age"] >= 40) & (df["age"] < 50)]),
                    len(df[(df["age"] >= 50) & (df["age"] < 60)]),
                    len(df[df["age"] >= 60]),
                ],
            },
        }

    def _format_notification_message(self, results: Dict[str, Any]) -> str:
        """Format the notification message with key findings."""
        message = f"Your diabetes analysis is complete!\n\n"
        message += f"Key Findings:\n"
        message += f"- Analyzed {results['data_points']} data points\n"

        if results["risk_factors"]:
            message += "\nRisk Factors Identified:\n"
            for factor in results["risk_factors"]:
                message += f"- {factor['factor']}: {factor['value']} (Threshold: {factor['threshold']})\n"

        message += "\nPlease log in to your dashboard to view detailed analysis and recommendations."
        return message
