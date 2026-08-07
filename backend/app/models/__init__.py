"""模型包：集中导入所有表模型，保证 SQLModel.metadata 能发现它们。"""

from app.models.post import Post
from app.models.task import Task
from app.models.user import User

__all__ = ["Post", "Task", "User"]
