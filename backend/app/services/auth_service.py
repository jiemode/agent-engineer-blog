"""用户业务：注册、登录。"""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister


def register_user(payload: UserRegister, session: Session) -> User:
    """注册：用户名唯一，密码只存哈希。"""
    exists = session.exec(select(User).where(User.username == payload.username)).first()
    if exists:
        raise HTTPException(status_code=409, detail="用户名已存在")
    user = User(username=payload.username, password_hash=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def login_user(payload: UserLogin, session: Session) -> str:
    """登录：校验密码，签发 JWT。"""
    user = session.exec(select(User).where(User.username == payload.username)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return create_access_token(user.id)
