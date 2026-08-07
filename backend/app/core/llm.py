"""大模型 Provider。

为什么单独一层：业务不需要知道用的是 DeepSeek 还是 OpenAI，只要调用
chat_completion / stream_chat_completion。换模型只改 .env，不改代码。
"""

import json

import httpx

from app.core.config import settings

SYSTEM_PROMPT = (
    "你是个人博客的 AI 助理。回答必须优先依据用户提供的资料片段，"
    "不要编造资料里没有的事实。使用简体中文，回答要简洁有结构。"
)


def llm_ready() -> bool:
    return bool(settings.llm_base_url and settings.llm_api_key and settings.llm_model)


def chat_completion(messages: list[dict]) -> str:
    """非流式调用：一次拿完整回答。"""
    if not llm_ready():
        raise RuntimeError("LLM 未配置")

    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
    payload = {"model": settings.llm_model, "messages": messages}

    with httpx.Client(timeout=60) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]


def stream_chat_completion(messages: list[dict]):
    """流式调用：逐块返回内容，让前端产生打字机效果。"""
    if not llm_ready():
        raise RuntimeError("LLM 未配置")

    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
    payload = {"model": settings.llm_model, "messages": messages, "stream": True}

    with httpx.Client(timeout=60) as client:
        with client.stream("POST", url, headers=headers, json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if not data_str or data_str == "[DONE]":
                    continue
                chunk = json.loads(data_str)
                choices = chunk.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                content = delta.get("content")
                if content:
                    yield content
