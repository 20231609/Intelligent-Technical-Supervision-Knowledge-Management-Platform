# repository/user_repo.py
"""用户数据访问层"""
from config.database import get_db

def get_user_by_username(username: str):
    """通过用户名获取用户"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.username, u.phone, u.display_name, u.password_hash,
                       u.phone_verified, r.name as role_name
                FROM users u JOIN roles r ON u.role_id = r.id
                WHERE u.username = %s AND u.is_active = TRUE AND u.deleted_flag = FALSE
            """, (username,))
            return cursor.fetchone()

def get_user_by_phone(phone: str):
    """通过手机号获取用户"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.username, u.phone, u.display_name, u.password_hash,
                       u.phone_verified, r.name as role_name
                FROM users u JOIN roles r ON u.role_id = r.id
                WHERE u.phone = %s AND u.is_active = TRUE AND u.deleted_flag = FALSE
            """, (phone,))
            return cursor.fetchone()

def create_user(username, password_hash, phone, display_name, role_id):
    """创建用户"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users 
                (username, password_hash, phone, phone_verified, display_name, 
                 avatar_url, role_id, is_active, last_login_at, last_login_ip, login_count)
                VALUES (%s, %s, %s, FALSE, %s, NULL, %s, TRUE, NULL, NULL, 0)
            """, (username, password_hash, phone, display_name, role_id))
            return cursor.lastrowid

def update_user_login(user_id: int):
    """更新用户登录信息"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET last_login_at = NOW(), login_count = login_count + 1 WHERE id = %s",
                (user_id,)
            )

def check_username_exists(username: str):
    """检查用户名是否存在"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s AND deleted_flag = FALSE", (username,))
            return cursor.fetchone() is not None

def check_phone_exists(phone: str):
    """检查手机号是否存在"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE phone = %s AND deleted_flag = FALSE", (phone,))
            return cursor.fetchone() is not None

def get_role_by_name(role_name: str):
    """通过角色名获取角色"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
            return cursor.fetchone()