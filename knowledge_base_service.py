# service/knowledge_base_service.py
"""知识库业务逻辑"""
import json
import os
from repository import knowledge_base_repo, document_repo, chunk_repo, tag_repo, status_log_repo
from service import milvus_service
from config.app_config import log_operation

def list_knowledge_bases_service(type_filter=None, keyword=None, page=1, page_size=20):
    """知识库列表服务"""
    return knowledge_base_repo.list_knowledge_bases(type_filter, keyword, page, page_size)

def get_knowledge_base_detail(kb_id: int):
    """获取知识库详情"""
    return knowledge_base_repo.get_knowledge_base_by_id(kb_id)

def create_knowledge_base_service(name, description, kb_type, segment_strategy, search_strategy, user_id):
    """创建知识库服务"""
    type_name_map = {
        "regulation": "规程规范",
        "tech_report": "技术报告论文",
        "term_entry": "术语条目",
        "general": "通用文档"
    }
    type_name = type_name_map.get(kb_type, "通用文档")
    kb_id = knowledge_base_repo.create_knowledge_base(
        name, description, kb_type, type_name, 
        segment_strategy, search_strategy, user_id
    )
    log_operation(user_id, "kb_create", f"创建知识库: {name} (ID:{kb_id})", kb_id=kb_id)
    return kb_id

def update_knowledge_base_service(kb_id: int, updates: dict, user_id: int):
    """更新知识库服务"""
    old_kb = knowledge_base_repo.get_kb_strategy(kb_id)
    if not old_kb:
        return None, "知识库不存在"

    # 构建更新字段
    db_updates = {"updated_at": "NOW()"}
    if "name" in updates:
        db_updates["name"] = updates["name"]
    if "description" in updates:
        db_updates["description"] = updates["description"]
    if "segment_strategy" in updates:
        db_updates["segment_strategy"] = json.dumps(updates["segment_strategy"])
    if "search_strategy" in updates:
        db_updates["search_strategy"] = json.dumps(updates["search_strategy"])

    knowledge_base_repo.update_knowledge_base(kb_id, db_updates)

    strategy_changed = "segment_strategy" in updates or "search_strategy" in updates
    reprocess_count = 0

    if strategy_changed:
        # 删除Milvus向量
        milvus_service.milvus_delete_by_kb(kb_id)
        
        # 重置文档状态
        reprocess_count = knowledge_base_repo.reset_kb_docs(kb_id)
        
        # 删除旧切片
        knowledge_base_repo.delete_kb_chunks(kb_id)
        
        # 重置切片计数
        knowledge_base_repo.update_kb_chunk_count(kb_id, 0)

        log_operation(user_id, "kb_update", 
            f"更新知识库(ID:{kb_id})策略，触发{reprocess_count}个文档重新处理", kb_id=kb_id)

        # 触发重新处理
        from config.app_config import executor
        import asyncio
        from service.document_pipeline import process_document_pipeline
        docs = knowledge_base_repo.get_kb_docs_by_status(kb_id, "uploaded")
        for doc in docs:
            executor.submit(asyncio.run, process_document_pipeline(doc["id"]))
    else:
        log_operation(user_id, "kb_update", f"更新知识库(ID:{kb_id})基本信息", kb_id=kb_id)

    return strategy_changed, reprocess_count

def delete_knowledge_base_service(kb_id: int, user_id: int):
    """删除知识库服务"""
    # 删除Milvus向量
    milvus_service.milvus_delete_by_kb(kb_id)
    
    # 删除文件
    docs = document_repo.get_documents_by_kb(kb_id)
    for doc in docs:
        if doc["file_path"] and os.path.exists(doc["file_path"]):
            os.remove(doc["file_path"])
    
    # 删除关联数据
    chunk_repo.delete_chunks_by_kb(kb_id)
    tag_repo.delete_tags_by_kb(kb_id)
    status_log_repo.delete_status_logs_by_kb(kb_id)
    
    # 删除文档和知识库
    doc_ids = document_repo.get_doc_ids_by_kb(kb_id)
    for doc_id in doc_ids:
        document_repo.delete_document(doc_id)
    knowledge_base_repo.delete_knowledge_base(kb_id)
    
    log_operation(user_id, "kb_delete", f"删除知识库 ID:{kb_id}", kb_id=kb_id)
    return True

def batch_delete_knowledge_bases_service(kb_ids: list, user_id: int):
    """批量删除知识库服务"""
    for kb_id in kb_ids:
        delete_knowledge_base_service(kb_id, user_id)
    log_operation(user_id, "kb_batch_delete", f"批量删除知识库: {kb_ids}")
    return len(kb_ids)