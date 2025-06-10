from app.models.diabetes import Base as DiabetesBase
from app.models.health import Base as HealthBase
from app.models.user import Base as UserBase

# Combine all metadata
metadata = [DiabetesBase.metadata, HealthBase.metadata, UserBase.metadata]
