from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.settings import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.logger import logger


def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == user_data.username).first()
        if user:
            logger.error(f"User {user_data.username} already exists.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
            )

        new_user = User(
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        token = create_access_token({"sub": new_user.username})
        logger.info(f"User {new_user.username} registered successfully.")

        return token
    except Exception as e:
        logger.error(f"Error registering user {user_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}",
        )


def login_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == user_data.username).first()
        if not user or not verify_password(user_data.password, user.hashed_password):
            logger.error(f"Invalid credentials for user {user_data.username}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
            )

        token = create_access_token({"sub": user.username})
        logger.info(f"User {user.username} logged in successfully.")

        return token
    except Exception as e:
        logger.error(f"Error logging in user {user_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging in user: {str(e)}",
        )
