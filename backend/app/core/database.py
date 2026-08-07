"""数据库基础设施。

engine 是全局单例（连接池），session 每个请求一个（事务边界清晰）。
get_session 是 FastAPI 依赖：请求进来时创建会话，请求结束自动关闭。

支持两种数据库：
- 本地开发默认 SQLite：零安装，数据存在 blog.db；
- 生产环境使用 PostgreSQL：把 DATABASE_URL 改成
  postgresql+psycopg://...（例如 Neon 的连接串），数据云端持久化。
"""

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# SQLite 需要关闭“只能本线程访问”的限制；PostgreSQL 不需要这个参数，
# 传了反而会报错，所以按 URL 前缀区分。
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args)


def create_db_and_tables() -> None:
    """根据 SQLModel 模型自动建表（开发期方便，生产用 Alembic 迁移）。"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """为每个请求提供一个数据库会话。"""
    with Session(engine) as session:
        yield session
