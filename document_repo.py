# repository/document_repo.py
"""文档数据访问层"""
import json
import os
from config.database import get_db

def list_documents(kb_id: int, status=None, keyword=None, page=1, page_size=20):
    """文档列表查询"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            conditions = ["d.kb_id = %s", "d.deleted_flag = FALSE"]
            params = [kb_id]

            if status:
                conditions.append("d.status = %s")
                params.append(status)

            if keyword:
                conditions.append("d.filename LIKE %s")
                params.append(f"%{keyword}%")

            where_clause = "WHERE " + " AND ".join(conditions)

            cursor.execute(f"SELECT COUNT(*) as total FROM documents d {where_clause}", tuple(params))
            total = cursor.fetchone()["total"]

            offset = (page - 1) * page_size
            sql = f"""
                SELECT d.id, d.kb_id, d.filename, d.file_size, d.file_type,
                       d.status, d.status_msg, d.chunk_count, d.tags, d.created_at,
                       d.updated_at, kb.name as kb_name
                FROM documents d
                JOIN knowledge_bases kb ON d.kb_id = kb.id
                {where_clause}
                ORDER BY d.created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, tuple(params + [page_size, offset]))
            docs = cursor.fetchall()

            for doc in docs:
                if doc["tags"]:
                    doc["tags"] = json.loads(doc["tags"]) if isinstance(doc["tags"], str) else doc["tags"]

            return {"list": docs, "total": total, "page": page, "page_size": page_size}

def get_document_by_id(doc_id: int):
    """获取文档详情"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT d.*, kb.segment_strategy, kb.search_strategy 
                FROM documents d 
                JOIN knowledge_bases kb ON d.kb_id = kb.id 
                WHERE d.id = %s
            """, (doc_id,))
            return cursor.fetchone()

def create_document(kb_id, filename, file_path, file_size, file_type, status, tags):
    """创建文档记录"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO documents (kb_id, filename, file_path, file_size, file_type, 
                                      status, status_msg, chunk_count, tags)
                VALUES (%s, %s, %s, %s, %s, %s, NULL, 0, %s)
            """, (kb_id, filename, file_path, file_size, file_type, status, json.dumps(tags)))
            return cursor.lastrowid

def update_document_status(doc_id: int, status: str, status_msg: str = None, chunk_count: int = None):
    """更新文档状态"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            updates = ["status = %s"]
            params = [status]
            if status_msg is not None:
                updates.append("status_msg = %s")
                params.append(status_msg)
            if chunk_count is not None:
                updates.append("chunk_count = %s")
                params.append(chunk_count)
            params.append(doc_id)
            cursor.execute(f"UPDATE documents SET {', '.join(updates)} WHERE id = %s", tuple(params))

def update_document_tags(doc_id: int, tags: list):
    """更新文档标签"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE documents SET tags = %s WHERE id = %s", (json.dumps(tags), doc_id))

def update_document_parsed_content(doc_id: int, parsed_content: str):
    """更新文档解析内容"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE documents SET parsed_content = %s WHERE id = %s", (parsed_content, doc_id))

def delete_document(doc_id: int):
    """删除文档"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))

def get_document_file_path(doc_id: int):
    """获取文档文件路径"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT file_path FROM documents WHERE id = %s", (doc_id,))
            result = cursor.fetchone()
            return result["file_path"] if result else None

def get_documents_by_kb(kb_id: int):
    """获取知识库下所有文档"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT file_path FROM documents WHERE kb_id = %s", (kb_id,))
            return cursor.fetchall()

def increment_kb_doc_count(kb_id: int):
    """增加知识库文档计数"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE knowledge_bases SET doc_count = doc_count + 1 WHERE id = %s", (kb_id,))

def get_document_chunks(doc_id: int, keyword=None, page=1, page_size=10):
    """获取文档切片"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            conditions = ["doc_id = %s", "deleted_flag = FALSE"]
            params = [doc_id]

            if keyword:
                conditions.append("content LIKE %s")
                params.append(f"%{keyword}%")

            where_clause = "WHERE " + " AND ".join(conditions)

            cursor.execute(f"SELECT COUNT(*) as total FROM chunks {where_clause}", tuple(params))
            total = cursor.fetchone()["total"]

            offset = (page - 1) * page_size
            sql = f"""
                SELECT id, chunk_index, heading_path, heading_level, content, 
                       content_length, page_number, vector_id, created_at, embedding_status
                FROM chunks
                {where_clause}
                ORDER BY chunk_index
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, tuple(params + [page_size, offset]))
            return {"list": cursor.fetchall(), "total": total, "page": page, "page_size": page_size}

def get_doc_info(doc_id: int):
    """获取文档基本信息"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, filename, status, chunk_count, file_size, file_type
                FROM documents WHERE id = %s AND deleted_flag = FALSE
            """, (doc_id,))
            return cursor.fetchone()

def batch_delete_documents(doc_ids: list):
    """批量删除文档"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            placeholders = ",".join(["%s"] * len(doc_ids))
            # 获取文件路径
            cursor.execute(f"SELECT file_path FROM documents WHERE id IN ({placeholders})", tuple(doc_ids))
            files = cursor.fetchall()
            # 删除文档
            cursor.execute(f"DELETE FROM documents WHERE id IN ({placeholders})", tuple(doc_ids))
            return files

def get_doc_ids_by_kb(kb_id: int):
    """获取知识库下所有文档ID"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM documents WHERE kb_id = %s", (kb_id,))
            return [row["id"] for row in cursor.fetchall()]