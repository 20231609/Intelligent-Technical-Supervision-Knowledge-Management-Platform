# config/database.py
"""数据库配置与连接管理"""
import pymysql
import pymysql.cursors
from contextlib import contextmanager

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "111111",
    "database": "power_knowledge_management",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

@contextmanager
def get_db():
    """数据库连接上下文管理器"""
    conn = None
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"],
            cursorclass=DB_CONFIG["cursorclass"],
            autocommit=True
        )
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()