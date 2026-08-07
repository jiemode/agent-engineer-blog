"""用户表模型。"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str  # 永远只存哈希，不存明文
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
