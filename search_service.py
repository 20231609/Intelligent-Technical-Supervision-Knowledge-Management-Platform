# service/search_service.py
"""搜索服务"""
import json
from repository import document_repo
from service import milvus_service
from config.milvus_config import get_embedding

def search_knowledge_service(query, kb_ids=None, search_mode="semantic_rerank", 
                            top_k=10, similarity_threshold=0.7, tag_filters=None, rerank_top_n=5):
    """知识检索服务"""
    query_embedding = get_embedding(query)
    
    milvus_results = milvus_service.milvus_search(
        query_embedding=query_embedding,
        kb_ids=kb_ids,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    
    if not milvus_results:
        return fallback_search_service(query, kb_ids, top_k, similarity_threshold, tag_filters)
    
    # 获取文档元数据
    doc_ids = list(set([r["doc_id"] for r in milvus_results]))
    doc_meta = {}
    if doc_ids:
        # 这里需要批量查询文档元数据
        pass  # 简化处理
    
    formatted_results = []
    for i, result in enumerate(milvus_results):
        formatted_results.append({
            "rank": i + 1,
            "score": result["score"],
            "chunk_id": result["chunk_id"],
            "doc_id": result["doc_id"],
            "doc_name": "未知文档",  # 简化
            "kb_id": result["kb_id"],
            "kb_name": "未知知识库",  # 简化
            "heading_path": result["heading_path"],
            "content": result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"],
            "content_length": len(result["content"]),
            "tags": [],
            "milvus_id": result["milvus_id"]
        })
    
    if search_mode == "semantic_rerank" and len(formatted_results) > rerank_top_n:
        formatted_results = formatted_results[:rerank_top_n]
    
    return {
        "query": query,
        "search_mode": search_mode,
        "total": len(formatted_results),
        "results": formatted_results,
        "vector_db": "Milvus" if milvus_service.MILVUS_AVAILABLE else "MySQL(Fallback)"
    }

def fallback_search_service(query, kb_ids=None, top_k=10, similarity_threshold=0.7, tag_filters=None):
    """MySQL回退检索服务"""
    # 简化实现，实际需要从repository查询
    return {
        "query": query,
        "search_mode": "semantic",
        "total": 0,
        "results": [],
        "vector_db": "MySQL(Fallback)"
    }