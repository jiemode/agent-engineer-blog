"""AI 助理路由：聊天 + 流式聊天。"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.assistant import AssistantRequest
from app.services import assistant_service

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat")
def assistant_chat(
    payload: AssistantRequest,
    _current_user: User = Depends(get_current_user),
):
    return assistant_service.chat(payload.message, payload.history)


@router.post("/chat/stream")
def assistant_chat_stream(
    payload: AssistantRequest,
    _current_user: User = Depends(get_current_user),
):
    return StreamingResponse(
        assistant_service.chat_stream(payload.message, payload.history),
        media_type="application/x-ndjson",
    )
