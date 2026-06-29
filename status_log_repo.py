# repository/status_log_repo.py
"""文档状态日志数据访问层"""
from config.database import get_db

def create_status_log(doc_id: int, from_status: str, to_status: str, message: str):
    """创建状态变更日志"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO doc_status_logs (doc_id, from_status, to_status, message, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (doc_id, from_status, to_status, message))

def get_status_logs_by_doc(doc_id: int):
    """获取文档状态日志"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT from_status, to_status, message, created_at
                FROM doc_status_logs
                WHERE doc_id = %s
                ORDER BY created_at DESC
            """, (doc_id,))
            return cursor.fetchall()

def delete_status_logs_by_kb(kb_id: int):
    """删除知识库下所有状态日志"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM doc_status_logs 
                WHERE doc_id IN (SELECT id FROM documents WHERE kb_id = %s)
            """, (kb_id,))

def delete_status_logs_by_doc_ids(doc_ids: list):
    """批量删除文档状态日志"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            placeholders = ",".join(["%s"] * len(doc_ids))
            cursor.execute(f"""
                DELETE FROM doc_status_logs 
                WHERE doc_id IN ({placeholders})
            """, tuple(doc_ids))