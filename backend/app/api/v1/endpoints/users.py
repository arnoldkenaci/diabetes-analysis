from typing import Any

from app.core.database import get_session
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(get_session),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    # Check if user with this email already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )

    # Create new user
    user = User(
        name=user_in.name,
        surname=user_in.surname,
        email=user_in.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
