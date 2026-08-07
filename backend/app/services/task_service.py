"""任务业务：创建任务、查询状态。"""

from fastapi import HTTPException

from app.core.task_engine import enqueue_task, get_task
from app.models.task import Task


def create_summarize_task(post_id: int) -> Task:
    return enqueue_task("post.summarize", {"post_id": post_id})


def get_task_status(task_id: int) -> dict:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {
        "task_id": task.id,
        "task_type": task.task_type,
        "status": task.status,
        "result": task.result,
        "error": task.error,
    }
