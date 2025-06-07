from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from ..services.analysis import AnalysisService
from ..services.notification import NotificationService
from ..core.config import get_settings

settings = get_settings()


class AnalysisScheduler:
    """Scheduler for periodic analysis."""

    def __init__(self, db: Session):
        self.db = db
        self.analysis_service = AnalysisService(db)
        self.notification_service = NotificationService()
        self.last_run: Optional[datetime] = None

    async def run_periodic_analysis(self) -> None:
        """Run analysis periodically."""
        current_time = datetime.now()

        # Check if it's time to run analysis
        if self.last_run is None or current_time - self.last_run > timedelta(
            minutes=settings.ANALYSIS_INTERVAL_MINUTES
        ):
            # Run analysis
            results = await self.analysis_service.run_analysis()
            insights = await self.analysis_service.get_insights()

            # Check if we need to send notifications
            if self._should_send_notification(insights):
                await self.notification_service.send_notification(
                    {
                        "type": "analysis_alert",
                        "timestamp": current_time.isoformat(),
                        "insights": insights,
                        "recommendations": results["recommendations"],
                    }
                )

            self.last_run = current_time

    def _should_send_notification(self, insights: dict) -> bool:
        """Check if notification should be sent based on insights."""
        risk_factors = insights["insights"]["risk_factors"]
        return (
            risk_factors["high_glucose"]
            or risk_factors["obesity"]
            or insights["insights"]["age_risk"] is not None
            or insights["insights"]["bmi_risk"] is not None
        )
