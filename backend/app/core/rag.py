"""RAG 检索基础设施（当前是词法版，后续可升级向量检索）。

RAG = 先检索再生成。这里负责"检索"：
1. 把 knowledge/ 里的 Markdown 笔记切成块；
2. jieba 中文分词；
3. 建倒排索引（词 → 块）；
4. 查询时按词频打分，返回 Top-K。

为什么分块：整篇塞给模型会超过上下文、增加成本、还容易被无关内容干扰。
"""

import re
from pathlib import Path

import jieba

# 项目根目录下的 knowledge 文件夹（app/core/rag.py 向上 3 层）。
KNOWLEDGE_DIR = Path(__file__).resolve().parents[3] / "knowledge"

chunks: list[dict] = []
inverted_index: dict[str, list[tuple[int, int]]] = {}


def load_notes() -> list[tuple[str, str]]:
    if not KNOWLEDGE_DIR.exists():
        return []
    result = []
    # 用 rglob 递归读取 knowledge/ 下所有 Markdown，
    # 这样 digital-garden 导入的多级目录也能被检索到。
    for file in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        title = file.relative_to(KNOWLEDGE_DIR).with_suffix("").as_posix()
        result.append((title, file.read_text(encoding="utf-8")))
    return result


def split_into_chunks(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """按长度切块，块与块之间保留重叠，避免语义被切断。"""
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) <= size:
        return [text] if text else []
    parts = []
    start = 0
    while start < len(text):
        end = start + size
        parts.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return [part for part in parts if part]


def tokenize(text: str) -> list[str]:
    """jieba 中文分词，去掉单字噪声。"""
    words = [w.strip() for w in jieba.lcut(text) if w.strip()]
    return [w for w in words if len(w) > 1]


def build_index() -> None:
    """启动时构建内存索引。笔记不变时索引也不需要重建。"""
    global chunks, inverted_index
    chunks = []
    inverted_index = {}
    for title, text in load_notes():
        for part in split_into_chunks(text):
            chunk_id = len(chunks)
            tokens = tokenize(part)
            chunks.append({"id": chunk_id, "title": title, "text": part})
            for word in set(tokens):
                count = tokens.count(word)
                inverted_index.setdefault(word, []).append((chunk_id, count))


def search(query: str, top_k: int = 5) -> list[dict]:
    """按词频打分，返回最相关的 Top-K 块。"""
    query_words = set(tokenize(query))
    scores: dict[int, int] = {}
    for word in query_words:
        for chunk_id, count in inverted_index.get(word, []):
            scores[chunk_id] = scores.get(chunk_id, 0) + count
    ranked = sorted(scores.items(), key=lambda item: -item[1])
    return [chunks[chunk_id] for chunk_id, _ in ranked[:top_k]]
