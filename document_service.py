# service/document_service.py
"""文档业务逻辑服务"""
import os
import json
import shutil
import uuid
from repository import document_repo, chunk_repo, tag_repo, status_log_repo, knowledge_base_repo, daily_stats_repo
from service import milvus_service, document_parser
from config.app_config import log_operation, UPLOAD_DIR

def list_documents_service(kb_id: int, status=None, keyword=None, page=1, page_size=20):
    """文档列表服务"""
    return document_repo.list_documents(kb_id, status, keyword, page, page_size)

def upload_document_service(file, kb_id: int, tags: str, user_id: int):
    """上传文档服务"""
    allowed_types = ["pdf", "docx", "pptx", "xlsx", "md", "txt", "png", "jpg", "jpeg", "gif", "bmp", "webp"]
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in allowed_types:
        raise ValueError(f"不支持的文件类型: {file_ext}")

    file_name = f"{uuid.uuid4().hex[:16]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    doc_id = document_repo.create_document(kb_id, file.filename, file_path, file_size, file_ext, "uploaded", tag_list)
    
    # 创建标签
    tag_repo.create_document_tags(doc_id, tag_list)
    
    # 增加文档计数
    knowledge_base_repo.increment_kb_doc_count(kb_id)
    
    # 记录日志
    log_operation(user_id, "doc_upload", f"上传文档: {file.filename} (ID:{doc_id})", kb_id=kb_id, doc_id=doc_id)
    
    # 增加统计
    daily_stats_repo.increment_doc_upload_count()
    
    return {
        "id": doc_id, 
        "filename": file.filename, 
        "status": "uploaded", 
        "kb_id": kb_id, 
        "tags": tag_list
    }

def update_document_tags_service(doc_id: int, tags: list, user_id: int):
    """编辑文档标签服务"""
    document_repo.update_document_tags(doc_id, tags)
    
    # 同步更新document_tags表
    tag_repo.delete_document_tags(doc_id)
    tag_repo.create_document_tags(doc_id, tags)
    
    log_operation(user_id, "doc_update_tags", f"更新文档(ID:{doc_id})标签", doc_id=doc_id)
    return True

def retry_document_service(doc_id: int, user_id: int):
    """重试文档处理服务"""
    doc = document_repo.get_document_by_id(doc_id)
    if not doc:
        raise ValueError("文档不存在")
    
    # 删除旧切片
    chunk_repo.delete_chunks_by_doc(doc_id)
    
    # 删除Milvus向量
    milvus_service.milvus_delete_by_doc(doc_id)
    
    # 重置状态
    document_repo.update_document_status(doc_id, "uploaded", "用户触发重新处理", 0)
    
    # 记录状态变更
    status_log_repo.create_status_log(doc_id, doc["status"], "uploaded", "用户触发重新处理")
    
    log_operation(user_id, "doc_retry", f"重试文档处理: {doc['filename']} (ID:{doc_id})", 
                  kb_id=doc["kb_id"], doc_id=doc_id)
    
    # 触发重新处理
    from config.app_config import executor
    import asyncio
    from service.document_pipeline import process_document_pipeline
    executor.submit(asyncio.run, process_document_pipeline(doc_id))
    
    return True

def batch_delete_documents_service(doc_ids: list, user_id: int):
    """批量删除文档服务"""
    # 获取文件路径
    files = document_repo.batch_delete_documents(doc_ids)
    
    # 删除物理文件
    for file in files:
        if file["file_path"] and os.path.exists(file["file_path"]):
            os.remove(file["file_path"])
    
    # 删除Milvus向量
    for doc_id in doc_ids:
        milvus_service.milvus_delete_by_doc(doc_id)
    
    # 删除切片
    for doc_id in doc_ids:
        chunk_repo.delete_chunks_by_doc(doc_id)
    
    # 删除标签
    tag_repo.delete_tags_by_doc_ids(doc_ids)
    
    # 删除状态日志
    status_log_repo.delete_status_logs_by_doc_ids(doc_ids)
    
    log_operation(user_id, "doc_batch_delete", f"批量删除文档: {doc_ids}")
    return len(doc_ids)

def get_document_chunks_service(doc_id: int, keyword=None, page=1, page_size=10):
    """获取文档切片服务"""
    doc_info = document_repo.get_doc_info(doc_id)
    if not doc_info:
        raise ValueError("文档不存在")
    
    chunks_data = document_repo.get_document_chunks(doc_id, keyword, page, page_size)
    chunks_data["doc_info"] = doc_info
    return chunks_data

def get_document_status_logs_service(doc_id: int):
    """获取文档状态日志服务"""
    return status_log_repo.get_status_logs_by_doc(doc_id)