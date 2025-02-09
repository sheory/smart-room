from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.settings import get_db
from app.schemas.user import Token, UserCreate
from app.services.auth_service import login_user, register_user

auth_router = APIRouter()


@auth_router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    token = register_user(user_data, db)

    return {"access_token": token, "token_type": "bearer"}


@auth_router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    token = login_user(user_data, db)

    return {"access_token": token, "token_type": "bearer"}
