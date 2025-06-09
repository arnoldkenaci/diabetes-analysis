from app.core.database import get_session
from app.schemas.diabetes import InsightsResult
from app.services.insights import InsightsService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=InsightsResult)
async def get_insights(db: Session = Depends(get_session)):
    """Get insights from the dataset."""
    insights_service = InsightsService(db)
    return insights_service.get_insights()
