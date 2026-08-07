"""认证路由。"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.user import UserLogin, UserRegister
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(payload: UserRegister, session: Session = Depends(get_session)):
    user = auth_service.register_user(payload, session)
    return {"id": user.id, "username": user.username}


@router.post("/login")
def login(payload: UserLogin, session: Session = Depends(get_session)):
    access_token = auth_service.login_user(payload, session)
    return {"access_token": access_token, "token_type": "bearer"}
