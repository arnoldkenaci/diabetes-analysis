import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models import DiabetesRecord
from sqlalchemy.orm import sessionmaker
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# Kaggle credentials
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_KEY = os.getenv("KAGGLE_KEY")

# Database configuration
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "dataset_analysis")

# Dataset details
DATASET_NAME = "uciml/pima-indians-diabetes-database"
FILE_NAME = "diabetes.csv"


def download_dataset():
    # kaggle needs to be imported after load_env()
    import kaggle

    """Download the dataset from Kaggle."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Download the dataset
        logger.info("Downloading dataset from Kaggle...")
        kaggle.api.dataset_download_file(DATASET_NAME, FILE_NAME, path="data")
        logger.info("Dataset downloaded successfully!")
    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        raise


def process_data():
    """Process the dataset and load it into the database."""
    try:
        # Read the CSV file
        file_path = os.path.join("data", FILE_NAME)
        df = pd.read_csv(file_path)

        # Print column names to debug
        logger.info("Dataset columns:")
        logger.info(df.columns.tolist())

        # Create database connection
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        Session = sessionmaker(bind=engine)
        session = Session()

        # Process data in chunks
        chunk_size = 100
        total_rows = len(df)

        logger.info(f"Processing {total_rows} records...")

        for i in range(0, total_rows, chunk_size):
            chunk = df.iloc[i : i + chunk_size]
            records = []

            for _, row in chunk.iterrows():
                record = DiabetesRecord(
                    pregnancies=row["Pregnancies"],
                    glucose=row["Glucose"],
                    blood_pressure=row["BloodPressure"],
                    skin_thickness=row["SkinThickness"],
                    insulin=row["Insulin"],
                    bmi=row["BMI"],
                    diabetes_pedigree=row["DiabetesPedigreeFunction"],
                    age=row["Age"],
                    outcome=bool(row["Outcome"]),
                )
                records.append(record)

            session.bulk_save_objects(records)
            session.commit()

            logger.info(
                f"Processed {min(i + chunk_size, total_rows)}/{total_rows} records"
            )

        logger.info("Data processing completed successfully!")

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise
    finally:
        session.close()


def main():
    """Main function to download and process the dataset."""
    try:
        download_dataset()
        process_data()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise


if __name__ == "__main__":
    main()
