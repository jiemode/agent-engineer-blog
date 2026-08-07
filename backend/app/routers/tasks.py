"""异步任务路由。"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/summarize", status_code=201)
def create_summarize_task(
    payload: TaskCreate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    task = task_service.create_summarize_task(payload.post_id)
    return {"task_id": task.id, "status": task.status}


@router.get("/{task_id}")
def get_task_status(
    task_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    return task_service.get_task_status(task_id)
