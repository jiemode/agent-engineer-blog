"""博客文章表模型。"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str  # Markdown 正文
    tags: str = ""  # 简单方案：逗号分隔存字符串，后续可拆关联表
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
