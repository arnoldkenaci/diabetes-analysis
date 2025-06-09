import uuid
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Optional

import pandas as pd
from app.models.diabetes import DataSource, DiabetesRecord, UserAttempt
from app.services.base import BaseService
from fastapi import HTTPException, UploadFile


class DataService(BaseService[DiabetesRecord]):
    def get_records(
        self,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        min_bmi: Optional[float] = None,
        max_bmi: Optional[float] = None,
        min_glucose: Optional[float] = None,
        max_glucose: Optional[float] = None,
        outcome: Optional[bool] = None,
    ) -> List[DiabetesRecord]:
        """Get diabetes records with optional filters."""
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
                query = query.filter(DiabetesRecord.diabetes == outcome)

            return query.all()

    def process_upload(
        self, file_content: bytes, filename: str, user_id: str
    ) -> Dict[str, Any]:
        """Process uploaded CSV file and store records."""
        with self.get_session() as db:
            # Create a new user attempt record
            attempt_id = str(uuid.uuid4())
            user_attempt = UserAttempt(
                id=attempt_id,
                user_id=user_id,
                filename=filename,
                records_count=0,
                status="processing",
            )
            db.add(user_attempt)
            db.commit()

            try:
                # Read the CSV file
                df = pd.read_csv(StringIO(file_content.decode("utf-8")))

                # Validate required columns
                required_columns = [
                    "Pregnancies",
                    "Glucose",
                    "BloodPressure",
                    "SkinThickness",
                    "Insulin",
                    "BMI",
                    "DiabetesPedigreeFunction",
                    "Age",
                ]
                missing_columns = [
                    col for col in required_columns if col not in df.columns
                ]
                if missing_columns:
                    self._update_attempt_status(
                        user_attempt,
                        "failed",
                        f"Missing required columns: {', '.join(missing_columns)}",
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required columns: {', '.join(missing_columns)}",
                    )

                # Convert DataFrame to records
                records = []
                for _, row in df.iterrows():
                    record = DiabetesRecord(
                        id=str(uuid.uuid4()),
                        pregnancies=int(row["Pregnancies"]),
                        glucose=int(row["Glucose"]),
                        blood_pressure=int(row["BloodPressure"]),
                        skin_thickness=int(row["SkinThickness"]),
                        insulin=int(row["Insulin"]),
                        bmi=float(row["BMI"]),
                        diabetes_pedigree=float(row["DiabetesPedigreeFunction"]),
                        age=int(row["Age"]),
                        source=DataSource.USER_UPLOAD,
                        user_attempt_id=attempt_id,
                    )
                    records.append(record)

                # Save records to database
                db.add_all(records)

                # Update user attempt record
                self._update_attempt_status(user_attempt, "success", None, len(records))

                return {
                    "message": f"Successfully uploaded {len(records)} records",
                    "records_uploaded": len(records),
                    "attempt_id": attempt_id,
                }

            except pd.errors.EmptyDataError:
                self._update_attempt_status(
                    user_attempt, "failed", "The uploaded file is empty"
                )
                raise HTTPException(
                    status_code=400, detail="The uploaded file is empty"
                )
            except pd.errors.ParserError:
                self._update_attempt_status(
                    user_attempt, "failed", "Invalid CSV format"
                )
                raise HTTPException(status_code=400, detail="Invalid CSV format")
            except Exception as e:
                self._update_attempt_status(user_attempt, "failed", str(e))
                raise HTTPException(
                    status_code=500, detail=f"Error processing file: {str(e)}"
                )

    def get_attempt_records(self, attempt_id: str) -> List[Dict[str, Any]]:
        """Get records for a specific upload attempt."""
        with self.get_session() as db:
            records = (
                db.query(DiabetesRecord)
                .filter(DiabetesRecord.user_attempt_id == attempt_id)
                .all()
            )

            return [
                {
                    "id": record.id,
                    "glucose": record.glucose,
                    "bmi": record.bmi,
                    "age": record.age,
                    "diabetes": record.diabetes,
                    "source": record.source,
                    "created_at": record.created_at,
                }
                for record in records
            ]

    def _update_attempt_status(
        self,
        attempt: UserAttempt,
        status: str,
        error_message: Optional[str] = None,
        records_count: Optional[int] = None,
    ) -> None:
        """Update the status of a user attempt."""
        with self.get_session() as db:
            attempt.status = status
            if error_message is not None:
                attempt.error_message = error_message
            if records_count is not None:
                attempt.records_count = records_count
            attempt.completed_at = datetime.utcnow()
            db.commit()

    async def upload_data(self, file: UploadFile, user_id: str) -> UserAttempt:
        """Upload and process diabetes data file."""
        try:
            # Create user attempt record
            attempt_id = str(uuid.uuid4())
            attempt = UserAttempt(
                id=attempt_id,
                user_id=user_id,
                filename=file.filename,
                records_count=0,
                status="processing",
            )

            with self.get_session() as db:
                db.add(attempt)
                db.commit()

                # Read and process the file
                df = pd.read_csv(file.file)
                records = []

                for _, row in df.iterrows():
                    record = DiabetesRecord(
                        id=str(uuid.uuid4()),  # Generate UUID for each record
                        pregnancies=int(row.get("pregnancies", 0)),
                        glucose=int(row.get("glucose", 0)),
                        blood_pressure=int(row.get("blood_pressure", 0)),
                        skin_thickness=int(row.get("skin_thickness", 0)),
                        insulin=int(row.get("insulin", 0)),
                        bmi=float(row.get("bmi", 0.0)),
                        diabetes_pedigree=float(row.get("diabetes_pedigree", 0.0)),
                        age=int(row.get("age", 0)),
                        outcome=bool(row.get("outcome", False)),
                        source=DataSource.USER_UPLOAD,
                        user_attempt_id=attempt_id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    records.append(record)

                # Save records
                db.bulk_save_objects(records)

                # Update attempt status
                attempt.records_count = len(records)
                attempt.status = "completed"
                attempt.completed_at = datetime.utcnow()
                db.commit()

                return attempt

        except Exception as e:
            # Update attempt status on error
            with self.get_session() as db:
                attempt.status = "failed"
                attempt.error_message = str(e)
                attempt.completed_at = datetime.utcnow()
                db.commit()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_user_attempts(self) -> List[UserAttempt]:
        """Get all attempts for a user."""
        with self.get_session() as db:
            return db.query(UserAttempt).order_by(UserAttempt.created_at.desc()).all()

    async def get_attempt_data(self, attempt_id: str) -> List[DiabetesRecord]:
        """Get all records for a specific attempt."""
        with self.get_session() as db:
            return (
                db.query(DiabetesRecord)
                .filter(DiabetesRecord.user_attempt_id == attempt_id)
                .all()
            )

    async def get_user_data(self, user_id: str) -> List[DiabetesRecord]:
        """Get all records for a user."""
        with self.get_session() as db:
            return (
                db.query(DiabetesRecord)
                .join(UserAttempt)
                .filter(UserAttempt.user_id == user_id)
                .all()
            )
