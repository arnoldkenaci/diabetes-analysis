from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base schema for user data."""

    name: str
    surname: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""

    pass


class UserUpdate(UserBase):
    """Schema for updating a user."""

    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    """Schema for user data as stored in the database."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserResponse(UserInDB):
    """Schema for user data returned to the client."""

    pass
