"""RAG 检索路由：公开可查。"""

from fastapi import APIRouter

from app.services import rag_service

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/search")
def rag_search(q: str = ""):
    if not q.strip():
        return {"query": q, "results": []}
    return {"query": q, "results": rag_service.search_knowledge(q, top_k=5)}
