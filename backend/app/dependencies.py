"""共享依赖。

FastAPI 的 Depends 是"依赖注入"：路由只需要声明需要什么，
框架负责准备好。这里放所有路由共享的依赖，比如当前登录用户。
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_session
from app.core.security import decode_access_token
from app.models.user import User

# auto_error=False：拿不到 Token 时不直接抛错，由我们自己决定怎么返回。
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """门卫依赖：验证 JWT，返回当前用户；失败抛 401。"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="请先登录")
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期或无效")
    user = session.get(User, int(payload.get("sub", "0")))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
