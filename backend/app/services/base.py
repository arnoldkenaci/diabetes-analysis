from contextlib import contextmanager
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseService(Generic[T]):
    """Base service class with common database session handling."""

    def __init__(self, db: Session):
        self.db = db

    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        try:
            yield self.db
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def commit(self):
        """Commit the current session."""
        self.db.commit()

    def rollback(self):
        """Rollback the current session."""
        self.db.rollback()
