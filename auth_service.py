# service/auth_service.py
"""认证业务逻辑服务"""
import uuid
from datetime import datetime
from repository import user_repo
from config.app_config import active_tokens, log_operation

def login_service(username=None, phone=None, password=None):
    """登录服务"""
    if phone and not username:
        user = user_repo.get_user_by_phone(phone)
    else:
        user = user_repo.get_user_by_username(username)

    if not user or password != user["password_hash"]:
        return None, "用户名/手机号或密码错误"

    token = f"token_{user['id']}_{uuid.uuid4().hex[:16]}"
    active_tokens[token] = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role_name"],
        "login_at": datetime.now().isoformat()
    }

    user_repo.update_user_login(user["id"])
    log_operation(user["id"], "login", f"用户 {user['username']} 登录成功")

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "phone": user["phone"],
            "phone_verified": user["phone_verified"],
            "display_name": user["display_name"],
            "role": user["role_name"]
        }
    }, None

def register_service(username, password, phone=None, display_name=None):
    """注册服务"""
    if user_repo.check_username_exists(username):
        return None, "用户名已存在"

    if phone and user_repo.check_phone_exists(phone):
        return None, "手机号已被注册"

    role = user_repo.get_role_by_name("standard_user")
    if not role:
        return None, "系统错误：默认角色不存在"

    user_id = user_repo.create_user(username, password, phone, display_name or username, role["id"])

    return {
        "id": user_id,
        "username": username,
        "phone": phone,
        "display_name": display_name or username,
        "role": "standard_user"
    }, None

def verify_token_service(token: str):
    """验证Token服务"""
    if not token:
        raise ValueError("缺少认证Token")
    if token not in active_tokens:
        raise ValueError("Token无效或已过期")
    return active_tokens[token]

def require_admin_service(token: str):
    """要求管理员权限"""
    user = verify_token_service(token)
    if user.get("role") not in ["admin", "super_admin"]:
        raise ValueError("需要管理员权限")
    return user

def logout_service(token: str):
    """登出服务"""
    if token in active_tokens:
        user = active_tokens[token]
        log_operation(user["id"], "logout", f"用户 {user['username']} 登出")
        del active_tokens[token]
    return True