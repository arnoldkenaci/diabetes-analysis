from io import StringIO
from typing import List, Optional

import pandas as pd
from app.core.database import get_session
from app.models.diabetes import DiabetesRecord
from app.schemas.diabetes import DiabetesRecordCreate
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/data", response_model=List[DiabetesRecordCreate])
async def get_data(
    db: Session = Depends(get_session),
    min_age: Optional[int] = Query(None, description="Minimum age filter"),
    max_age: Optional[int] = Query(None, description="Maximum age filter"),
    min_bmi: Optional[float] = Query(None, description="Minimum BMI filter"),
    max_bmi: Optional[float] = Query(None, description="Maximum BMI filter"),
    min_glucose: Optional[float] = Query(
        None, description="Minimum glucose level filter"
    ),
    max_glucose: Optional[float] = Query(
        None, description="Maximum glucose level filter"
    ),
    outcome: Optional[bool] = Query(None, description="Filter by diabetes outcome"),
):
    """Get diabetes dataset with optional filters."""
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
        query = query.filter(DiabetesRecord.diabetes == outcome)

    records = query.all()
    return records


@router.post("/upload")
async def upload_data(file: UploadFile = File(...), db: Session = Depends(get_session)):
    """Upload diabetes dataset."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        # Read the CSV file
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))

        # Validate required columns
        required_columns = ["glucose", "bmi", "age", "diabetes"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}",
            )

        # Convert DataFrame to records
        records = []
        for _, row in df.iterrows():
            record = DiabetesRecord(
                glucose=int(row["glucose"]),
                bmi=float(row["bmi"]),
                age=int(row["age"]),
                diabetes=bool(row["diabetes"]),
            )
            records.append(record)

        # Save records to database
        db.add_all(records)
        db.commit()

        return {
            "message": f"Successfully uploaded {len(records)} records",
            "records_uploaded": len(records),
        }

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
