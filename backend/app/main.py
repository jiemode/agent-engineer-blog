"""应用入口。

职责：
1. 创建 FastAPI 实例；
2. 挂载统一路由；
3. 在 lifespan 里完成启动初始化（建表、建 RAG 索引、启动任务 Worker）。

为什么这样设计：main.py 只做"组装"，不写业务。业务拆到 routers/services，
保证每个文件职责单一，这也是 AnonForge 的分层方式。
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.rag import build_index
from app.core.task_engine import run_worker
from app.routers.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化，退出时清理。"""
    create_db_and_tables()
    build_index()
    worker = asyncio.create_task(run_worker())
    yield
    worker.cancel()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS：允许 GitHub Pages 上的前端跨域调用本后端。
# 学习项目先放开所有来源；上线稳定后可以改成具体域名，例如
# ["https://jiemode.github.io"]。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
