"""AI 助理请求模型。"""

from pydantic import BaseModel


class AssistantRequest(BaseModel):
    message: str
    history: list[dict] = []  # 多轮对话历史，前端负责保存并随请求带回
