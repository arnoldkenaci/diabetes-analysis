from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ....core.database import get_session
from ....models.diabetes import DiabetesRecord
from ....schemas.diabetes import DiabetesRecordList

router = APIRouter()


@router.get("/", response_model=DiabetesRecordList)
async def get_data(
    db: Session = Depends(get_session),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    outcome: Optional[bool] = None,
):
    """Get diabetes records with optional filters."""
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
