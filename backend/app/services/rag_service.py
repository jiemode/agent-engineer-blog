"""检索业务：把核心检索能力包一层，路由不直接碰 core。"""

from app.core.rag import search


def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    return search(query, top_k=top_k)
