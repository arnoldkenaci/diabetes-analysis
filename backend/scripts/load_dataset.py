#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.dataset import DatasetManager
from app.core.load_data import load_dataset_to_db
from app.core.database import engine
from app.models.diabetes import Base


def main():
    """Download and load the diabetes dataset."""
    print("Setting up database...")
    Base.metadata.create_all(bind=engine)

    print("Initializing dataset manager...")
    dataset_manager = DatasetManager()

    print("Downloading dataset...")
    dataset_path = dataset_manager.download_dataset("diabetes")

    if not dataset_path:
        print("Error: Failed to download dataset")
        sys.exit(1)

    print(f"Dataset downloaded to: {dataset_path}")

    print("Loading dataset into database...")
    load_dataset_to_db()
    print("Dataset loaded successfully!")


if __name__ == "__main__":
    main()
