# service/material_service.py
"""素材业务逻辑服务"""
import os
import json
import shutil
import uuid
from repository import material_repo
from config.app_config import log_operation, UPLOAD_DIR

def list_materials_service(type_filter=None, keyword=None, page=1, page_size=20):
    """素材列表服务"""
    return material_repo.list_materials(type_filter, keyword, page, page_size)

def upload_material_service(file, name, type, description, tags, user_id):
    """上传素材服务"""
    file_name = f"{uuid.uuid4().hex[:16]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    file_ext = file.filename.split(".")[-1].lower()

    material_id = material_repo.create_material(name, type, file_path, file_size, file_ext, description, user_id)

    if tags:
        try:
            tag_dict = json.loads(tags)
            # 这里需要保存素材标签
        except:
            pass

    log_operation(user_id, "material_upload", f"上传素材: {name} (ID:{material_id})")
    return material_id

def update_material_tags_service(material_id: int, tags: dict, user_id: int):
    """更新素材标签服务"""
    # 这里需要实现标签更新逻辑
    log_operation(user_id, "material_update_tags", f"更新素材(ID:{material_id})标签")
    return True

def delete_material_service(material_id: int, user_id: int):
    """删除素材服务"""
    file_path = material_repo.get_material_file_path(material_id)
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    material_repo.delete_material(material_id)
    log_operation(user_id, "material_delete", f"删除素材 ID:{material_id}")
    return True