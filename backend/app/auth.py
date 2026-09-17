import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException

from app.config import ADMIN_PASSWORD, SECRET_KEY, TOKEN_EXPIRE_HOURS

ALGORITHM = "HS256"


def verify_password(password: str) -> bool:
    """定时安全比较，避免根据响应时间猜密码

    注意：compare_digest 对含非 ASCII 字符的 str 会抛 TypeError，
    所以必须先 encode 成 bytes —— 否则管理员密码设成中文时登录接口会 500。
    """
    if not ADMIN_PASSWORD:
        return False
    return secrets.compare_digest(password.encode(), ADMIN_PASSWORD.encode())


def create_token() -> str:
    """签发登录令牌"""
    payload = {"exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def require_admin(authorization: str = Header(default="")) -> None:
    """FastAPI 依赖：校验 Authorization: Bearer <token>，不通过直接 401"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")

    try:
        jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="登录状态无效")
