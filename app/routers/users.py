from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse, Token
from app.auth import create_access_token, get_current_user
from app.logger import logger

router = APIRouter(prefix="/user", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user (first time join).

    - **telegram_id**: Telegram user ID
    - **display_name**: User's display name
    """
    try:
        # Check if user already exists
        existing_user = (
            db.query(User).filter(User.telegram_id == user_data.telegram_id).first()
        )
        if existing_user:
            logger.warning(
                f"User already exists with telegram_id: {user_data.telegram_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this telegram_id already exists",
            )

        # Create new user
        new_user = User(
            telegram_id=user_data.telegram_id, display_name=user_data.display_name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(
            f"User created: id={new_user.id}, telegram_id={new_user.telegram_id}"
        )
        return new_user

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint violation",
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("", response_model=UserResponse)
def update_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's display name (requires authentication).

    - **display_name**: New display name
    """
    try:
        current_user.display_name = user_data.display_name
        db.commit()
        db.refresh(current_user)

        logger.info(
            f"User updated: id={current_user.id}, new_name={current_user.display_name}"
        )
        return current_user

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's information."""
    logger.info(f"User info retrieved: id={current_user.id}")
    return current_user


@router.get("/{telegram_id}", response_model=UserResponse)
def get_user_by_telegram_id(telegram_id: str, db: Session = Depends(get_db)):
    """
    Get user by Telegram ID (public endpoint).

    - **telegram_id**: Telegram user ID
    """
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        logger.warning(f"User not found: telegram_id={telegram_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    logger.info(f"User retrieved: id={user.id}, telegram_id={telegram_id}")
    return user


@router.post("/token", response_model=Token)
def login(telegram_id: str, db: Session = Depends(get_db)):
    """
    Generate access token for a user.

    - **telegram_id**: Telegram user ID
    """
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        logger.warning(f"Login failed: user not found with telegram_id={telegram_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    access_token = create_access_token(data={"sub": user.telegram_id})
    logger.info(f"Token generated for user: id={user.id}, telegram_id={telegram_id}")

    return {"access_token": access_token, "token_type": "bearer"}
