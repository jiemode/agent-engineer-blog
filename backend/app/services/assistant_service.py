"""助理业务：包装 Agent 核心，路由只负责 HTTP。"""

from app.core.assistant import run_assistant, stream_assistant


def chat(message: str, history: list[dict]) -> dict:
    return run_assistant(message, history)


def chat_stream(message: str, history: list[dict]):
    return stream_assistant(message, history)
