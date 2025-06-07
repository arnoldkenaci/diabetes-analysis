from app.core.database import get_session
from app.services.analysis import AnalysisService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()
analysis_service = AnalysisService(db=get_session())


@router.get("/analyze")
async def analyze_data(db: Session = Depends(get_session)):
    """Run analysis on the dataset."""
    analysis_service.db = db
    return await analysis_service.run_analysis()
