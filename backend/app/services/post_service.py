"""文章业务：增删改查。"""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.post import Post
from app.schemas.post import BlogPostCreate, BlogPostUpdate


def list_posts(session: Session) -> list[Post]:
    return session.exec(select(Post).order_by(Post.id.desc())).all()


def get_post(session: Session, post_id: int) -> Post:
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post


def create_post(session: Session, payload: BlogPostCreate) -> Post:
    db_post = Post(
        title=payload.title,
        content=payload.content,
        tags=",".join(payload.tags),
    )
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


def update_post(session: Session, post_id: int, payload: BlogPostUpdate) -> Post:
    db_post = get_post(session, post_id)
    db_post.title = payload.title
    db_post.content = payload.content
    db_post.tags = ",".join(payload.tags)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


def delete_post(session: Session, post_id: int) -> None:
    db_post = get_post(session, post_id)
    session.delete(db_post)
    session.commit()
