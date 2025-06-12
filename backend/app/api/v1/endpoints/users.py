from typing import Any

from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(get_session),
    user_in: UserCreate,
    response: Response,
) -> Any:
    """
    Create new user.
    """
    # Check if user with this email already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        # Set 409 status code
        response.status_code = 409
        # Return existing user
        return UserResponse(**user.__dict__)

    # Create new user
    user = User(
        name=user_in.name,
        surname=user_in.surname,
        email=user_in.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Return user
    return UserResponse(**user.__dict__)
