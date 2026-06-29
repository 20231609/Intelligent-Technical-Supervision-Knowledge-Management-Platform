# repository/knowledge_base_repo.py
"""知识库数据访问层"""
import json
from config.database import get_db

def list_knowledge_bases(type_filter=None, keyword=None, page=1, page_size=20):
    """知识库列表查询"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            conditions = ["kb.deleted_flag = FALSE"]
            params = []

            if type_filter:
                conditions.append("kb.type = %s")
                params.append(type_filter)

            if keyword:
                conditions.append("(kb.name LIKE %s OR kb.description LIKE %s)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])

            where_clause = "WHERE " + " AND ".join(conditions)

            cursor.execute(f"SELECT COUNT(*) as total FROM knowledge_bases kb {where_clause}", tuple(params))
            total = cursor.fetchone()["total"]

            offset = (page - 1) * page_size
            sql = f"""
                SELECT kb.id, kb.name, kb.description, kb.type, kb.type_name,
                       kb.doc_count, kb.chunk_count,
                       kb.segment_strategy, kb.search_strategy,
                       u.username as created_by, kb.created_at, kb.updated_at
                FROM knowledge_bases kb
                JOIN users u ON kb.created_by = u.id
                {where_clause}
                ORDER BY kb.created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, tuple(params + [page_size, offset]))
            kb_list = cursor.fetchall()

            for kb in kb_list:
                if kb["segment_strategy"]:
                    kb["segment_strategy"] = json.loads(kb["segment_strategy"]) if isinstance(kb["segment_strategy"], str) else kb["segment_strategy"]
                if kb["search_strategy"]:
                    kb["search_strategy"] = json.loads(kb["search_strategy"]) if isinstance(kb["search_strategy"], str) else kb["search_strategy"]

            return {"list": kb_list, "total": total, "page": page, "page_size": page_size}

def get_knowledge_base_by_id(kb_id: int):
    """获取知识库详情"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT kb.*, u.username as created_by_name
                FROM knowledge_bases kb
                JOIN users u ON kb.created_by = u.id
                WHERE kb.id = %s AND kb.deleted_flag = FALSE
            """, (kb_id,))
            kb = cursor.fetchone()

            if kb:
                if kb.get("segment_strategy"):
                    kb["segment_strategy"] = json.loads(kb["segment_strategy"]) if isinstance(kb["segment_strategy"], str) else kb["segment_strategy"]
                if kb.get("search_strategy"):
                    kb["search_strategy"] = json.loads(kb["search_strategy"]) if isinstance(kb["search_strategy"], str) else kb["search_strategy"]

            return kb

def create_knowledge_base(name, description, kb_type, type_name, segment_strategy, search_strategy, created_by):
    """创建知识库"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO knowledge_bases 
                (name, description, type, type_name, segment_strategy, search_strategy, 
                 doc_count, chunk_count, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, 0, 0, %s)
            """, (name, description, kb_type, type_name, 
                  json.dumps(segment_strategy), json.dumps(search_strategy), created_by))
            return cursor.lastrowid

def update_knowledge_base(kb_id: int, updates: dict):
    """更新知识库"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            set_parts = []
            params = []
            for key, value in updates.items():
                set_parts.append(f"{key} = %s")
                params.append(value)
            params.append(kb_id)
            cursor.execute(f"UPDATE knowledge_bases SET {', '.join(set_parts)} WHERE id = %s", tuple(params))
            return cursor.rowcount

def delete_knowledge_base(kb_id: int):
    """删除知识库"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM knowledge_bases WHERE id = %s", (kb_id,))
            return cursor.rowcount

def get_kb_strategy(kb_id: int):
    """获取知识库策略"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT segment_strategy, search_strategy FROM knowledge_bases WHERE id = %s AND deleted_flag = FALSE", (kb_id,))
            return cursor.fetchone()

def get_kb_docs_by_status(kb_id: int, status: str):
    """获取知识库下指定状态的文档"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM documents WHERE kb_id = %s AND status = %s", (kb_id, status))
            return cursor.fetchall()

def reset_kb_docs(kb_id: int):
    """重置知识库下文档状态"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE documents SET status = 'uploaded', status_msg = '策略变更触发重新处理', 
                chunk_count = 0 WHERE kb_id = %s AND status = 'ready'
            """, (kb_id,))
            return cursor.rowcount

def delete_kb_chunks(kb_id: int):
    """删除知识库下所有切片"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM chunks WHERE kb_id = %s", (kb_id,))
            return cursor.rowcount

def update_kb_chunk_count(kb_id: int, chunk_count: int):
    """更新知识库切片计数"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE knowledge_bases SET chunk_count = %s WHERE id = %s", (chunk_count, kb_id))

            def increment_kb_doc_count(kb_id: int):
                """增加知识库文档计数"""
                with get_db() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            UPDATE knowledge_bases 
                            SET doc_count = doc_count + 1 
                            WHERE id = %s
                        """, (kb_id,))
                        return cursor.rowcount