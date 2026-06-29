# repository/chunk_repo.py
"""切片数据访问层"""
from config.database import get_db

def create_chunk(doc_id, kb_id, chunk_index, heading_path, heading_level, 
                 content, content_length, page_number, vector_id, embedding_status):
    """创建切片记录"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO chunks (doc_id, kb_id, chunk_index, heading_path, heading_level, 
                                  content, content_length, page_number, vector_id, embedding_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (doc_id, kb_id, chunk_index, heading_path, heading_level,
                  content, content_length, page_number, vector_id, embedding_status))
            return cursor.lastrowid

def update_chunk_vector_id(chunk_id: int, vector_id: str):
    """更新切片向量ID"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE chunks SET vector_id = %s WHERE id = %s", (vector_id, chunk_id))

def delete_chunks_by_doc(doc_id: int):
    """删除文档的所有切片"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM chunks WHERE doc_id = %s", (doc_id,))

def delete_chunks_by_kb(kb_id: int):
    """删除知识库的所有切片"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM chunks WHERE kb_id = %s", (kb_id,))

def get_chunks_by_doc(doc_id: int):
    """获取文档的所有切片"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM chunks WHERE doc_id = %s", (doc_id,))
            return cursor.fetchall()

def get_all_ready_chunks():
    """获取所有就绪状态的切片"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.id, c.doc_id, c.kb_id, c.content, c.heading_path, c.chunk_index
                FROM chunks c
                JOIN documents d ON c.doc_id = d.id
                WHERE d.status = 'ready' AND c.deleted_flag = FALSE
            """)
            return cursor.fetchall()