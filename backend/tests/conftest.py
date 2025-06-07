import pytest
from app.core.database import Base, SessionLocal, engine
from app.models.diabetes import DiabetesRecord


@pytest.fixture(scope="session")
def tables():
    """Create test tables."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(tables):
    """Create test database session."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_data(db_session):
    """Create sample diabetes records."""
    records = [
        DiabetesRecord(
            pregnancies=6,
            glucose=148,
            blood_pressure=72,
            skin_thickness=35,
            insulin=0,
            bmi=33.6,
            diabetes_pedigree=0.627,
            age=50,
            outcome=True,
        ),
        DiabetesRecord(
            pregnancies=1,
            glucose=85,
            blood_pressure=66,
            skin_thickness=29,
            insulin=0,
            bmi=26.6,
            diabetes_pedigree=0.351,
            age=31,
            outcome=False,
        ),
        DiabetesRecord(
            pregnancies=8,
            glucose=183,
            blood_pressure=64,
            skin_thickness=0,
            insulin=0,
            bmi=23.3,
            diabetes_pedigree=0.672,
            age=32,
            outcome=True,
        ),
    ]

    for record in records:
        db_session.add(record)
    db_session.commit()

    return records
