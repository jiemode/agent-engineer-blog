"""通用异步任务引擎（简化版）。

为什么需要它：AI 任务可能跑几分钟，HTTP 请求不能等。
设计：数据库存任务状态，一个 asyncio Worker 轮询 PENDING 任务执行。

这是 AnonForge 任务引擎的迷你版。工业版会升级为 Redis Stream 消息队列、
多 Worker、心跳、僵尸回收、死信表；状态机和注册表的思想完全一致。
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from sqlmodel import Session, select

from app.core.database import engine
from app.models.task import Task

Handler = Callable[[Session, dict[str, Any]], Awaitable[dict[str, Any]]]

handlers: dict[str, Handler] = {}


def register_handler(task_type: str):
    """注册表模式：新任务 = 一个带装饰器的函数，引擎无需改动。"""

    def decorator(func: Handler) -> Handler:
        handlers[task_type] = func
        return func

    return decorator


def enqueue_task(task_type: str, payload: dict[str, Any]) -> Task:
    """创建任务记录并返回，状态为 PENDING，等待 Worker 拾取。"""
    with Session(engine) as session:
        task = Task(task_type=task_type, payload=json.dumps(payload, ensure_ascii=False))
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def get_task(task_id: int) -> Task | None:
    with Session(engine) as session:
        return session.get(Task, task_id)


def _now():
    return datetime.now(timezone.utc)


async def process_one_task() -> bool:
    """取一条 PENDING 任务执行，返回是否处理了任务。"""
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.status == "PENDING").order_by(Task.id)
        ).first()
        if task is None:
            return False

        task.status = "RUNNING"
        task.started_at = _now()
        session.add(task)
        session.commit()

        payload = json.loads(task.payload or "{}")
        handler = handlers.get(task.task_type)
        try:
            if handler is None:
                raise ValueError(f"未注册任务处理器: {task.task_type}")
            result = await handler(session, payload)
            task.result = json.dumps(result, ensure_ascii=False)
            task.status = "SUCCEEDED"
        except Exception as exc:
            task.error = str(exc)
            task.status = "FAILED"
        task.finished_at = _now()
        session.add(task)
        session.commit()
        return True


async def run_worker():
    """后台 Worker 主循环：有任务就做，没任务就睡 0.5 秒。"""
    while True:
        handled = await process_one_task()
        if not handled:
            await asyncio.sleep(0.5)
