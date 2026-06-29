from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import Header, HTTPException

from src.config.settings import settings

_TOKENS: dict[str, dict] = {}
_USERS: dict[str, dict] = {
    settings.DEMO_ADMIN_USERNAME: {
        "password": settings.DEMO_ADMIN_PASSWORD,
        "role": "admin",
        "userId": "admin",
    }
}


def registerUser(username: str, password: str) -> dict:
    username = username.strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    if username in _USERS:
        raise HTTPException(status_code=400, detail="用户已存在")
    _USERS[username] = {"password": password, "role": "user", "userId": username}
    return {"username": username, "role": "user"}


def loginUser(username: str, password: str) -> dict:
    user = _USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = f"qa-{uuid4().hex}"
    _TOKENS[token] = {
        "userId": user["userId"],
        "username": username,
        "role": user["role"],
        "expiresAt": datetime.utcnow() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS),
    }
    return {"token": token, "access_token": token, "user": {"username": username, "role": user["role"]}}


def verifyCurrentUser(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或 token 无效")
    token = authorization.replace("Bearer ", "", 1).strip()
    state = _TOKENS.get(token)
    if not state:
        raise HTTPException(status_code=401, detail="未登录或 token 无效")
    if state["expiresAt"] < datetime.utcnow():
        _TOKENS.pop(token, None)
        raise HTTPException(status_code=401, detail="登录已过期")
    return {"userId": state["userId"], "username": state["username"], "role": state["role"]}


def requireAdmin(currentUser: dict) -> None:
    if currentUser.get("role") not in {"admin", "super_admin"}:
        raise HTTPException(status_code=403, detail="需要管理员权限")
