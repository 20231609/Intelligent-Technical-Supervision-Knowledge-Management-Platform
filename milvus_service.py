# service/milvus_service.py
"""Milvus向量服务"""
import json
from datetime import datetime
from config.milvus_config import milvus_client, MILVUS_AVAILABLE, MILVUS_CONFIG, get_embedding
from repository import chunk_repo

def milvus_search(query_embedding: list, kb_ids: list = None, 
                  top_k: int = 10, similarity_threshold: float = 0.7) -> list:
    """Milvus向量检索"""
    if not milvus_client or not MILVUS_AVAILABLE:
        return []

    try:
        collection_name = MILVUS_CONFIG["collection_name"]
        filter_expr = ""
        if kb_ids:
            kb_ids_str = ",".join([str(k) for k in kb_ids])
            filter_expr = f"kb_id in [{kb_ids_str}]"

        results = milvus_client.search(
            collection_name=collection_name,
            data=[query_embedding],
            filter=filter_expr,
            limit=top_k,
            output_fields=["chunk_id", "doc_id", "kb_id", "content", "heading_path", "chunk_index", "created_at"],
            search_params={"metric_type": MILVUS_CONFIG["metric_type"], "params": {"nprobe": 10}}
        )

        formatted = []
        for hits in results:
            for hit in hits:
                if hit["distance"] >= similarity_threshold:
                    formatted.append({
                        "chunk_id": hit["entity"]["chunk_id"],
                        "doc_id": hit["entity"]["doc_id"],
                        "kb_id": hit["entity"]["kb_id"],
                        "content": hit["entity"]["content"],
                        "heading_path": hit["entity"]["heading_path"],
                        "chunk_index": hit["entity"]["chunk_index"],
                        "score": round(float(hit["distance"]), 4),
                        "milvus_id": hit["id"]
                    })
        return formatted
    except Exception as e:
        print(f"Milvus检索失败: {e}")
        return []

def milvus_insert(data: list) -> bool:
    """向Milvus插入向量数据"""
    if not milvus_client or not MILVUS_AVAILABLE:
        return False
    try:
        milvus_client.insert(collection_name=MILVUS_CONFIG["collection_name"], data=data)
        return True
    except Exception as e:
        print(f"Milvus插入失败: {e}")
        return False

def milvus_delete_by_doc(doc_id: int) -> bool:
    """根据文档ID删除Milvus向量"""
    if not milvus_client or not MILVUS_AVAILABLE:
        return False
    try:
        milvus_client.delete(collection_name=MILVUS_CONFIG["collection_name"], filter=f"doc_id == {doc_id}")
        return True
    except Exception as e:
        print(f"Milvus删除失败: {e}")
        return False

def milvus_delete_by_kb(kb_id: int) -> bool:
    """根据知识库ID删除Milvus向量"""
    if not milvus_client or not MILVUS_AVAILABLE:
        return False
    try:
        milvus_client.delete(collection_name=MILVUS_CONFIG["collection_name"], filter=f"kb_id == {kb_id}")
        return True
    except Exception as e:
        print(f"Milvus删除失败: {e}")
        return False

def rebuild_milvus_index() -> int:
    """重建Milvus索引"""
    if not milvus_client or not MILVUS_AVAILABLE:
        return 0

    chunks = chunk_repo.get_all_ready_chunks()
    collection_name = MILVUS_CONFIG["collection_name"]
    milvus_client.delete(collection_name=collection_name, filter="id >= 0")

    batch_size = 100
    inserted = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        milvus_data = []
        for chunk in batch:
            embedding = get_embedding(chunk["content"])
            milvus_data.append({
                "id": str(uuid.uuid4()),
                "chunk_id": chunk["id"],
                "doc_id": chunk["doc_id"],
                "kb_id": chunk["kb_id"],
                "content": chunk["content"],
                "embedding": embedding,
                "heading_path": chunk["heading_path"],
                "chunk_index": chunk["chunk_index"],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        if milvus_data:
            milvus_insert(milvus_data)
            inserted += len(milvus_data)

    return inserted

def get_milvus_status() -> dict:
    """获取Milvus状态"""
    if not MILVUS_AVAILABLE or not milvus_client:
        return {"connected": False, "message": "pymilvus未安装或连接失败"}

    collection_name = MILVUS_CONFIG["collection_name"]
    stats = milvus_client.get_collection_stats(collection_name)

    return {
        "connected": True,
        "collection_name": collection_name,
        "vector_count": stats.get("row_count", 0),
        "dimension": MILVUS_CONFIG["dim"],
        "metric_type": MILVUS_CONFIG["metric_type"],
        "embedding_model": "sentence-transformers" if EMBEDDING_AVAILABLE else "random(fallback)",
        "embedding_dim": EMBEDDING_DIM
    }