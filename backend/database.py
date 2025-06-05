from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from models import Base

load_dotenv()


def create_database():
    """Create the database if it doesn't exist."""
    # Get database connection parameters
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "dataset_analysis")

    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=db_user, password=db_password, host=db_host, port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (db_name,),
        )
        exists = cursor.fetchone()

        if not exists:
            print(f"Creating database {db_name}...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database {db_name} created successfully!")
        else:
            print(f"Database {db_name} already exists.")

    except Exception as e:
        print(f"Error creating database: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def get_database_url():
    """Get database URL from environment variables."""
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "dataset_analysis")

    URL = f"postgresql://{db_user}:{db_password}@" f"{db_host}:{db_port}/{db_name}"
    return URL


def init_db():
    """Initialize database connection and create tables."""
    # First ensure database exists
    create_database()

    # Then create tables
    engine = create_engine(get_database_url())
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session."""
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    create_database()
