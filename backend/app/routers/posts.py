"""文章路由：读公开，写需要登录。"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.post import BlogPostCreate, BlogPostUpdate
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("")
def list_posts(session: Session = Depends(get_session)):
    return post_service.list_posts(session)


@router.get("/{post_id}")
def get_post(post_id: int, session: Session = Depends(get_session)):
    return post_service.get_post(session, post_id)


@router.post("", status_code=201)
def create_post(
    payload: BlogPostCreate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    return post_service.create_post(session, payload)


@router.put("/{post_id}")
def update_post(
    post_id: int,
    payload: BlogPostUpdate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    return post_service.update_post(session, post_id, payload)


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    post_service.delete_post(session, post_id)
    return {"deleted": True, "id": post_id}
