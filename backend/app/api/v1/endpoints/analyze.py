from app.core.database import get_session
from app.services.analysis import AnalysisService
from app.services.insights import InsightsService
from app.services.notification import NotificationService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/")
async def analyze_data(db: Session = Depends(get_session)):
    """Run analysis on the dataset."""
    insights_service = InsightsService(db=db)
    notification_service = NotificationService()
    analysis_service = AnalysisService(
        insights_service=insights_service, notification_service=notification_service
    )
    analysis_service.db = db
    return await analysis_service.run_analysis()
