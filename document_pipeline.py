# service/document_pipeline.py
"""文档处理管线服务"""
import asyncio
import json
import uuid
from datetime import datetime
from repository import document_repo, chunk_repo, knowledge_base_repo
from service import document_parser, milvus_service
from config.milvus_config import get_embedding, MILVUS_AVAILABLE, milvus_client
from config.app_config import parsing_semaphore

async def process_document_pipeline(doc_id: int):
    """文档处理管线：解析 -> 切片 -> 向量化 -> Milvus存储"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        with parsing_semaphore:
            doc = document_repo.get_document_by_id(doc_id)
            if not doc:
                return

            # 更新为解析状态
            document_repo.update_document_status(doc_id, "parsing", "正在解析文档内容...")

            try:
                parsed_content = document_parser.parse_document(doc["file_path"], doc["file_type"])
                if not parsed_content or len(parsed_content.strip()) == 0:
                    parsed_content = f"[文档内容为空或无法提取文本: {doc['filename']}]"
            except Exception as parse_err:
                document_repo.update_document_status(doc_id, "failed", f"解析失败: {str(parse_err)[:500]}")
                return

            # 更新为切片状态
            document_repo.update_document_parsed_content(doc_id, parsed_content[:65535])
            document_repo.update_document_status(doc_id, "slicing", "正在进行语义切片...")

            segment_strategy = json.loads(doc["segment_strategy"]) if isinstance(doc["segment_strategy"], str) else doc["segment_strategy"]
            strategy_type = segment_strategy.get("type", "heading")
            chunk_size = segment_strategy.get("chunk_size", 500)
            overlap = segment_strategy.get("overlap", 50)

            if strategy_type == "heading":
                chunks = document_parser.split_by_headings(parsed_content, chunk_size, overlap)
            else:
                chunks = document_parser.split_fixed(parsed_content, chunk_size, overlap)

            if not chunks:
                chunks = [{
                    "chunk_index": 0,
                    "heading_path": "全文",
                    "heading_level": 1,
                    "content": parsed_content[:2000],
                    "content_length": len(parsed_content[:2000]),
                    "page_number": None
                }]

            # 更新为向量化状态
            document_repo.update_document_status(doc_id, "embedding", "正在进行向量化...")

            milvus_data = []
            chunk_db_ids = []

            for chunk in chunks:
                embedding = get_embedding(chunk["content"])
                chunk_db_ids.append(None)
                milvus_data.append({
                    "id": str(uuid.uuid4()),
                    "chunk_id": 0,
                    "doc_id": doc_id,
                    "kb_id": doc["kb_id"],
                    "content": chunk["content"],
                    "embedding": embedding,
                    "heading_path": chunk["heading_path"],
                    "chunk_index": chunk["chunk_index"],
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            # 创建切片记录
            for idx, chunk in enumerate(chunks):
                chunk_id = chunk_repo.create_chunk(
                    doc_id, doc["kb_id"], chunk["chunk_index"], chunk["heading_path"],
                    chunk["heading_level"], chunk["content"], chunk["content_length"],
                    chunk.get("page_number"), None,
                    "completed" if MILVUS_AVAILABLE else "pending"
                )
                chunk_db_ids[idx] = chunk_id

                if idx < len(milvus_data):
                    milvus_data[idx]["chunk_id"] = chunk_id

            # 插入Milvus
            if milvus_data and MILVUS_AVAILABLE and milvus_client:
                milvus_service.milvus_insert(milvus_data)

                for idx, chunk_id in enumerate(chunk_db_ids):
                    if idx < len(milvus_data):
                        chunk_repo.update_chunk_vector_id(chunk_id, milvus_data[idx]["id"])

            # 更新为完成状态
            document_repo.update_document_status(doc_id, "ready", "处理完成", len(chunks))
            
            # 更新知识库切片计数
            knowledge_base_repo.update_kb_chunk_count(doc["kb_id"], 
                knowledge_base_repo.get_knowledge_base_by_id(doc["kb_id"])["chunk_count"] + len(chunks))

    except Exception as e:
        document_repo.update_document_status(doc_id, "failed", str(e)[:500])
    finally:
        loop.close()