"""总路由：统一 /api 前缀，并挂载所有业务路由。"""

from fastapi import APIRouter

from app.routers import assistant, auth, posts, rag, tasks

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(posts.router)
api_router.include_router(tasks.router)
api_router.include_router(rag.router)
api_router.include_router(assistant.router)


@api_router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
