"""异步任务表模型。"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_type: str = Field(index=True)
    status: str = "PENDING"  # PENDING -> RUNNING -> SUCCEEDED / FAILED
    payload: str = ""  # 任务参数，JSON 字符串
    result: str = ""  # 执行结果，JSON 字符串
    error: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    finished_at: datetime | None = None
