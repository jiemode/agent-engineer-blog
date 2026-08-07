"""任务相关请求模型。"""

from pydantic import BaseModel


class TaskCreate(BaseModel):
    post_id: int
