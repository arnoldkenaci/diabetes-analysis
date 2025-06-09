import pandas as pd
from sqlalchemy.orm import Session

from ..models.diabetes import DataSource, DiabetesRecord
from .database import SessionLocal
from .dataset import DatasetManager


def load_dataset_to_db(dataset_name: str = "diabetes") -> None:
    """Load dataset into database."""
    dataset_manager = DatasetManager()
    dataset_path = dataset_manager.get_dataset_path(dataset_name)

    if not dataset_path:
        raise FileNotFoundError(f"Dataset {dataset_name} not found")

    # Read CSV file
    df = pd.read_csv(dataset_path)

    # Print column names for debugging
    print("Available columns:", df.columns.tolist())

    # Map column names (handle case sensitivity and spaces)
    column_mapping = {
        "Pregnancies": "pregnancies",
        "Glucose": "glucose",
        "BloodPressure": "blood_pressure",
        "SkinThickness": "skin_thickness",
        "Insulin": "insulin",
        "BMI": "bmi",
        "DiabetesPedigreeFunction": "diabetes_pedigree",
        "Age": "age",
        "Outcome": "outcome",
    }

    # Rename columns to match our model
    df = df.rename(columns=column_mapping)

    # Create database session
    db = SessionLocal()
    try:
        # Convert DataFrame rows to DiabetesRecord objects
        records = [
            DiabetesRecord(
                pregnancies=row["pregnancies"],
                glucose=row["glucose"],
                blood_pressure=row["blood_pressure"],
                skin_thickness=row["skin_thickness"],
                insulin=row["insulin"],
                bmi=row["bmi"],
                diabetes_pedigree=row["diabetes_pedigree"],
                age=row["age"],
                outcome=bool(row["outcome"]),
                source=DataSource.DATASET,
            )
            for _, row in df.iterrows()
        ]

        # Add all records to database
        db.add_all(records)
        db.commit()
        print(f"Successfully loaded {len(records)} records into database")

    except Exception as e:
        db.rollback()
        print(f"Error details: {str(e)}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    dataset_manager = DatasetManager()
    dataset_manager.download_dataset("diabetes")
    load_dataset_to_db()
