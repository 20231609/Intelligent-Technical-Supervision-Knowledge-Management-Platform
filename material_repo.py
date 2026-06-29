# repository/material_repo.py
"""素材数据访问层"""
import json
from config.database import get_db

def list_materials(type_filter=None, keyword=None, page=1, page_size=20):
    """素材列表查询"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            conditions = ["m.deleted_flag = FALSE"]
            params = []

            if type_filter:
                conditions.append("m.type = %s")
                params.append(type_filter)

            if keyword:
                conditions.append("m.name LIKE %s")
                params.append(f"%{keyword}%")

            where_clause = "WHERE " + " AND ".join(conditions)

            cursor.execute(f"SELECT COUNT(*) as total FROM materials m {where_clause}", tuple(params))
            total = cursor.fetchone()["total"]

            offset = (page - 1) * page_size
            sql = f"""
                SELECT m.id, m.name, m.type, m.file_size, m.file_type, m.description,
                       u.username as created_by, m.created_at
                FROM materials m
                JOIN users u ON m.created_by = u.id
                {where_clause}
                ORDER BY m.created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, tuple(params + [page_size, offset]))
            materials = cursor.fetchall()

            for mat in materials:
                cursor.execute("SELECT tag_key, tag_value FROM material_tags WHERE material_id = %s AND deleted_flag = FALSE", (mat["id"],))
                tags = cursor.fetchall()
                mat["tags"] = {t["tag_key"]: t["tag_value"] for t in tags}

            return {"list": materials, "total": total, "page": page, "page_size": page_size}

def create_material(name, type, file_path, file_size, file_type, description, created_by):
    """创建素材"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO materials (name, type, file_path, file_size, file_type, description, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, type, file_path, file_size, file_type, description, created_by))
            return cursor.lastrowid

def get_material_by_id(material_id: int):
    """获取素材"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM materials WHERE id = %s", (material_id,))
            return cursor.fetchone()

def delete_material(material_id: int):
    """删除素材"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM materials WHERE id = %s", (material_id,))

def get_material_file_path(material_id: int):
    """获取素材文件路径"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT file_path FROM materials WHERE id = %s", (material_id,))
            result = cursor.fetchone()
            return result["file_path"] if result else None