"""文章相关请求模型。"""

from pydantic import BaseModel


class BlogPostCreate(BaseModel):
    title: str
    content: str
    tags: list[str] = []


class BlogPostUpdate(BaseModel):
    title: str
    content: str
    tags: list[str] = []
