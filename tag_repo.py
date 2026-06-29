# repository/tag_repo.py
"""标签数据访问层"""
from config.database import get_db

def create_document_tags(doc_id: int, tags: list):
    """创建文档标签"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            for tag in tags:
                cursor.execute("INSERT INTO document_tags (doc_id, tag_name) VALUES (%s, %s)", (doc_id, tag))

def delete_document_tags(doc_id: int):
    """删除文档标签"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM document_tags WHERE doc_id = %s", (doc_id,))

def get_document_tags(doc_id: int):
    """获取文档标签"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT tag_name FROM document_tags WHERE doc_id = %s", (doc_id,))
            return [row["tag_name"] for row in cursor.fetchall()]

def delete_tags_by_kb(kb_id: int):
    """删除知识库下所有文档标签"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM document_tags 
                WHERE doc_id IN (SELECT id FROM documents WHERE kb_id = %s)
            """, (kb_id,))

def delete_tags_by_doc_ids(doc_ids: list):
    """批量删除文档标签"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            placeholders = ",".join(["%s"] * len(doc_ids))
            cursor.execute(f"DELETE FROM document_tags WHERE doc_id IN ({placeholders})", tuple(doc_ids))