"""把 digital_garden 的全部文章导入 Agent Engineer Blog。

设计目标：
1. digital_garden 永远只读，不会被修改。
2. 文章进入 PostgreSQL/SQLite，变成博客可浏览的 Post。
3. 同一份 Markdown 复制到 knowledge/，让 RAG 助理也能检索。
4. 脚本可重复运行：标题相同的文章会被更新，不会重复创建。

运行方式（在 backend 目录）：
    uv run python scripts/import_digital_garden.py

如果需要导入别的笔记目录：
    $env:DIGITAL_GARDEN_DIR = "E:\\path\\to\\notes"
    uv run python scripts/import_digital_garden.py
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import Session, select

from app.core.database import engine
from app.models.post import Post

# 默认读取用户本机的 digital_garden；脚本只读，不会写入该目录。
GARDEN_DIR = Path(
    os.getenv("DIGITAL_GARDEN_DIR", r"E:\AI\Projects\digital_garden")
).resolve()

# knowledge 目录位于项目根目录：backend/scripts/import_digital_garden.py
# 向上两级是 backend，向上三级才是项目根目录。
KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge"
KNOWLEDGE_ROOT = KNOWLEDGE_DIR / "digital-garden"

# 这些是 VitePress 的示例/说明文件，不是真实学习文章，导入时跳过。
EXCLUDED_NAMES = {
    "README.md",
    "api-examples.md",
    "markdown-examples.md",
}

# VitePress 缓存、Obsidian 配置、Git 目录和依赖目录不是学习文章。
EXCLUDED_DIR_PARTS = {
    ".git",
    ".obsidian",
    ".pnpm-store",
    ".vitepress",
    "node_modules",
}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """解析 Markdown 开头的 --- frontmatter ---。

    只做轻量解析，不引入额外依赖：
    - 有 frontmatter 就返回 {字段: 值} 和去掉 frontmatter 的正文
    - 没有 frontmatter 就返回空字典和原文
    """
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return {}, text

    metadata: dict[str, str] = {}
    for line in lines[1:end_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")

    content = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return metadata, content


def title_from_filename(filename: str) -> str:
    """文件名兜底标题：去掉 .md 和前面的序号，再用空格代替短横线。"""
    name = Path(filename).stem
    name = re.sub(r"^\d+-", "", name)
    name = re.sub(r"[-_]+", " ", name)
    return name.strip()


def build_tags(source_relative: Path, title: str, content: str) -> list[str]:
    """把目录结构翻译成可筛选的标签。

    例如 projects/AnonForge/01-xxx.md 会得到：
    - projects
    - AnonForge
    - projects/AnonForge
    - digital-garden
    """
    parts = source_relative.parts[:-1]
    tags = ["digital-garden"]

    for part in parts:
        if part:
            tags.append(part)

    parent = source_relative.parent.as_posix()
    if parent != ".":
        tags.append(parent)

    if "面试" in title or "面试" in content[:500]:
        tags.append("面试")

    # 去重并限制数量，避免分类栏被无意义标签塞满。
    seen: set[str] = set()
    result: list[str] = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
    return result[:8]


def make_unique_title(candidate: str, used_titles: set[str], parent: str) -> str:
    """同名文章通过父目录区分，保证每一篇都能独立展示。"""
    if candidate not in used_titles:
        return candidate
    return f"{candidate}（{parent}）"


def collect_articles() -> list[dict]:
    """扫描 digital_garden 的所有 Markdown，返回结构化文章列表。"""
    articles: list[dict] = []
    used_titles: set[str] = set()

    for path in sorted(GARDEN_DIR.rglob("*.md")):
        relative_parts = path.relative_to(GARDEN_DIR).parts
        if any(part in EXCLUDED_DIR_PARTS for part in relative_parts):
            continue
        if path.name in EXCLUDED_NAMES:
            continue

        source_relative = path.relative_to(GARDEN_DIR)
        raw_text = path.read_text(encoding="utf-8")
        metadata, content = parse_frontmatter(raw_text)

        base_title = (
            metadata.get("title")
            or title_from_filename(path.name)
            or source_relative.stem
        )
        title = make_unique_title(
            base_title,
            used_titles,
            source_relative.parent.as_posix(),
        )
        used_titles.add(title)

        if not content.strip():
            content = metadata.get("description", "（这篇文章暂时只有标题。）")

        description = metadata.get("description", "")
        articles.append(
            {
                "title": title,
                "content": content,
                "tags": build_tags(source_relative, title, content),
                "source_relative": source_relative,
                "created_at": datetime.fromtimestamp(
                    path.stat().st_mtime,
                    tz=timezone.utc,
                ),
                "description": description,
            }
        )

    return articles


def sync_knowledge_files(articles: list[dict]) -> None:
    """把文章复制到 knowledge/digital-garden/，供 RAG 检索。"""
    copied = 0
    for article in articles:
        destination = KNOWLEDGE_ROOT / article["source_relative"]
        destination.parent.mkdir(parents=True, exist_ok=True)

        new_text = article["content"]
        if destination.exists() and destination.read_text(encoding="utf-8") == new_text:
            continue

        destination.write_text(new_text, encoding="utf-8")
        copied += 1

    print(f"知识库同步完成：新增/更新 {copied} 个文件，目录 {KNOWLEDGE_ROOT}")


def sync_database(articles: list[dict]) -> None:
    """把文章写入数据库；标题已存在的文章走更新逻辑。"""
    created = 0
    updated = 0

    with Session(engine) as session:
        for article in articles:
            existing = session.exec(
                select(Post).where(Post.title == article["title"])
            ).first()

            if existing is None:
                session.add(
                    Post(
                        title=article["title"],
                        content=article["content"],
                        tags=",".join(article["tags"]),
                        created_at=article["created_at"],
                    )
                )
                created += 1
            else:
                existing.content = article["content"]
                existing.tags = ",".join(article["tags"])
                existing.created_at = article["created_at"]
                session.add(existing)
                updated += 1

        session.commit()

    print(f"数据库同步完成：新建 {created} 篇，更新 {updated} 篇")


def main() -> None:
    if not GARDEN_DIR.exists():
        raise SystemExit(f"没有找到 digital_garden 目录：{GARDEN_DIR}")

    articles = collect_articles()
    print(f"发现 {len(articles)} 篇文章，来源：{GARDEN_DIR}")

    sync_knowledge_files(articles)
    sync_database(articles)

    sample = articles[0] if articles else None
    if sample:
        print(f"示例：{sample['title']} | tags={sample['tags']}")


if __name__ == "__main__":
    main()
