"""文章摘要任务处理器。

任务处理器通过注册表自动注册，业务代码无需改引擎。
真实项目这里会调用大模型生成摘要，目前用首行 + 字数模拟。
"""

import asyncio

from app.core.task_engine import register_handler
from app.models.post import Post


@register_handler("post.summarize")
async def summarize_post(session, payload):
    post_id = int(payload.get("post_id") or 0)
    post = session.get(Post, post_id)
    if post is None:
        raise ValueError("文章不存在")

    await asyncio.sleep(2)  # 模拟 AI 思考

    text = (post.content or "").strip()
    first_line = text.splitlines()[0] if text else ""
    return {
        "post_id": post_id,
        "summary": first_line,
        "word_count": len(text.split()),
    }
