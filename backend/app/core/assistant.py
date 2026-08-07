"""Agent 助理核心。

Agent 的最小循环：
1. 感知用户消息；
2. 调用工具（RAG 检索）；
3. 组装上下文（资料 + 历史 + 问题）；
4. 大脑输出（真实 LLM 或 mock 降级）；
5. 返回答案和出处。
"""

import json
import time

from app.core.llm import (
    SYSTEM_PROMPT,
    chat_completion,
    llm_ready,
    stream_chat_completion,
)
from app.core.rag import search


def run_assistant(message: str, history: list[dict]) -> dict:
    """非流式入口：一次调用返回完整回答。"""
    chunks = search(message, top_k=3)
    answer = generate_answer(message, chunks, history)
    return {
        "answer": answer,
        "sources": [
            {"title": chunk["title"], "snippet": chunk["text"][:120]}
            for chunk in chunks
        ],
    }


def build_context(chunks: list[dict]) -> str:
    """把检索到的资料拼成模型能读的上下文。"""
    if not chunks:
        return "没有检索到相关资料。"
    return "\n\n".join(
        f"资料《{chunk['title']}》：\n{chunk['text']}" for chunk in chunks
    )


def build_messages(
    message: str, chunks: list[dict], history: list[dict]
) -> list[dict]:
    """标准三段式消息：system 规则 + 历史上下文 + 当前问题。"""
    context = build_context(chunks)
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\n以下是检索到的资料：\n" + context,
        },
        *history,
        {"role": "user", "content": message},
    ]


def generate_answer(
    message: str, chunks: list[dict], history: list[dict]
) -> str:
    if not llm_ready():
        return mock_brain(message, chunks)

    messages = build_messages(message, chunks, history)
    try:
        return chat_completion(messages)
    except Exception as exc:
        return (
            mock_brain(message, chunks)
            + f"\n\n（提示：真实大模型调用失败，已回退到模拟回答。错误：{exc}）"
        )


def stream_assistant(message: str, history: list[dict]):
    """流式入口：每行一个 NDJSON 事件，边生成边发给前端。"""
    chunks = search(message, top_k=3)

    yield json.dumps(
        {
            "type": "sources",
            "sources": [
                {"title": chunk["title"], "snippet": chunk["text"][:120]}
                for chunk in chunks
            ],
        },
        ensure_ascii=False,
    ) + "\n"

    messages = build_messages(message, chunks, history)

    if llm_ready():
        try:
            full = ""
            for content in stream_chat_completion(messages):
                full += content
                yield json.dumps(
                    {"type": "delta", "content": content}, ensure_ascii=False
                ) + "\n"
            yield json.dumps(
                {"type": "done", "answer": full}, ensure_ascii=False
            ) + "\n"
            return
        except Exception as exc:
            yield json.dumps(
                {"type": "error", "detail": str(exc)}, ensure_ascii=False
            ) + "\n"
            return

    text = mock_brain(message, chunks)
    full = ""
    for char in text:
        full += char
        time.sleep(0.02)
        yield json.dumps(
            {"type": "delta", "content": char}, ensure_ascii=False
        ) + "\n"
    yield json.dumps(
        {"type": "done", "answer": full}, ensure_ascii=False
    ) + "\n"


def mock_brain(message: str, chunks: list[dict]) -> str:
    """没有配置真实 LLM 时的降级回答，保证链路始终可跑。"""
    if not chunks:
        return (
            "我在知识库里没有找到相关内容。"
            "你可以先把笔记放进 knowledge/ 文件夹，再问我一次。"
        )
    top = chunks[0]
    return (
        f"根据我的笔记《{top['title']}》，我找到一段相关的内容：\n\n"
        f"“{top['text'][:200]}…”\n\n"
        f"当前使用模拟大脑，配置真实大模型后我会用这些资料组织完整回答。"
    )
