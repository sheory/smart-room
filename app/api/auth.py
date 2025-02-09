from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import constants
from app.core.logger import logger
from app.db.settings import get_db
from app.schemas.user import Token, UserCreate
from app.services.auth_service import login_user, register_user

auth_router = APIRouter()


@auth_router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        token = register_user(user_data, db)
        logger.info(f"User {user_data.username} registered successfully.")
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.error(
            f"{constants.ERROR_REGISTERING_USER} {user_data.username}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{constants.ERROR_REGISTERING_USER}: {str(e)}",
        )


@auth_router.post("/login", response_model=Token)
def login(
    user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    try:
        token = login_user(user_data, db)
        logger.info(f"User {user_data.username} logged in successfully.")
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"{constants.ERROR_LOGGING_USER} {user_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{constants.ERROR_LOGGING_USER}: {str(e)}",
        )
