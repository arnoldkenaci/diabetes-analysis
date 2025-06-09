from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..services.analysis import AnalysisService
from ..services.insights import InsightsService
from ..services.notification import NotificationService

settings = get_settings()


class AnalysisScheduler:
    """Scheduler for background analysis tasks."""

    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService()
        self.analysis_service = AnalysisService(
            insights_service=InsightsService(db=db),
            notification_service=self.notification_service,
            db=db,
        )

    async def run_background_analysis(self, user_id: str, user_attempt_id: str) -> None:
        """Run analysis in background for user-uploaded data.

        Args:
            user_id: The ID of the user who uploaded the data
            user_attempt_id: The ID of the user's upload attempt
        """
        try:
            # Run analysis for the specific user's data
            results = await self.analysis_service.analyze_user_data(user_id)
            insights = await self.analysis_service.get_insights()

            # Send notification to the user
            message = (
                f"Your diabetes risk analysis is complete!\n"
                f"Risk Level: {results['risk_level']}\n"
                f"Key Findings: {results['key_findings']}\n"
                f"Recommendations: {results['recommendations']}"
            )

            await self.notification_service.send_notification(
                user_id=user_id,
                subject="Diabetes Risk Analysis Complete",
                message=message,
                data={
                    "risk_level": results["risk_level"],
                    "key_findings": results["key_findings"],
                    "recommendations": results["recommendations"],
                    "insights": insights,
                },
            )

        except Exception as e:
            # Log the error and notify the user
            error_message = f"An error occurred during analysis: {str(e)}"
            await self.notification_service.send_notification(
                user_id=user_id, subject="Analysis Error", message=error_message
            )
            raise e
