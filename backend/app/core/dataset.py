from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .config import get_settings

settings = get_settings()

load_dotenv("../.env")
import kaggle

# Dataset configuration
DATASET_CONFIG = {
    "diabetes": {
        "kaggle_dataset": "uciml/pima-indians-diabetes-database",
        "filename": "diabetes.csv",
        "columns": [
            "pregnancies",
            "glucose",
            "blood_pressure",
            "skin_thickness",
            "insulin",
            "bmi",
            "diabetes_pedigree",
            "age",
            "outcome",
        ],
    }
}


class DatasetManager:
    """Manages dataset operations."""

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    def setup_kaggle(self, username: str, key: str) -> None:
        """Setup Kaggle credentials."""
        kaggle.api.authenticate()

    def download_dataset(self, dataset_name: str) -> Optional[Path]:
        """Download dataset from Kaggle."""
        if dataset_name not in DATASET_CONFIG:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        config = DATASET_CONFIG[dataset_name]
        dataset_path = self.data_dir / config["filename"]

        if dataset_path.exists():
            return dataset_path

        try:
            kaggle.api.dataset_download_file(
                config["kaggle_dataset"], config["filename"], path=str(self.data_dir)
            )
            return dataset_path
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return None

    def get_dataset_path(self, dataset_name: str) -> Optional[Path]:
        """Get path to dataset file."""
        if dataset_name not in DATASET_CONFIG:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        config = DATASET_CONFIG[dataset_name]
        dataset_path = self.data_dir / config["filename"]

        return dataset_path if dataset_path.exists() else None
