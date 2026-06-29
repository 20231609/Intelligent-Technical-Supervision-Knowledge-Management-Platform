# config/milvus_config.py
"""Milvus向量数据库配置"""
import os
import numpy as np

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 设置模型缓存目录（使用Python默认位置）
DEFAULT_CACHE_DIR = os.path.expanduser('~/.cache')
os.environ['HF_HOME'] = os.path.join(DEFAULT_CACHE_DIR, 'huggingface')
os.environ['TRANSFORMERS_CACHE'] = os.path.join(DEFAULT_CACHE_DIR, 'huggingface')
os.environ['SENTENCE_TRANSFORMERS_HOME'] = os.path.join(DEFAULT_CACHE_DIR, 'torch', 'sentence_transformers')

# ============================================================
# Milvus 导入
# ============================================================
try:
    from pymilvus import (
        connections, Collection, FieldSchema, CollectionSchema, DataType,
        utility, MilvusClient, AnnSearchRequest, RRFRanker
    )
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False
    print("警告: pymilvus 未安装，将使用模拟向量检索。请运行: pip install pymilvus")


try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_MODEL = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    EMBEDDING_DIM = EMBEDDING_MODEL.get_embedding_dimension()
    EMBEDDING_AVAILABLE = True
    print(f"嵌入模型加载成功，维度: {EMBEDDING_DIM}")
except Exception as e:
    EMBEDDING_AVAILABLE = False
    EMBEDDING_DIM = 384
    EMBEDDING_MODEL = None
    print(f"警告: 嵌入模型加载失败 ({e})，将使用随机向量。")
    print("如需使用真实向量，请确保网络连接或模型已缓存。")

# ============================================================
# Milvus配置
# ============================================================
MILVUS_CONFIG = {
    "host": "localhost",
    "port": "19530",
    "collection_name": "knowledge_chunks",
    "dim": EMBEDDING_DIM,
    "metric_type": "COSINE"
}

# ============================================================
# Milvus 连接与集合管理
# ============================================================
milvus_client = None

def init_milvus():
    """初始化Milvus连接和集合"""
    global milvus_client
    if not MILVUS_AVAILABLE:
        print("Milvus不可用，跳过初始化")
        return False

    try:
        milvus_client = MilvusClient("./milvus_knowledge.db")
        collection_name = MILVUS_CONFIG["collection_name"]

        if not milvus_client.has_collection(collection_name):
            schema = milvus_client.create_schema(auto_id=False, enable_dynamic_field=True)
            schema.add_field(field_name="id", datatype=DataType.VARCHAR, max_length=64, is_primary=True)
            schema.add_field(field_name="chunk_id", datatype=DataType.INT64)
            schema.add_field(field_name="doc_id", datatype=DataType.INT64)
            schema.add_field(field_name="kb_id", datatype=DataType.INT64)
            schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=65535)
            schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=MILVUS_CONFIG["dim"])
            schema.add_field(field_name="heading_path", datatype=DataType.VARCHAR, max_length=512)
            schema.add_field(field_name="chunk_index", datatype=DataType.INT64)
            schema.add_field(field_name="created_at", datatype=DataType.VARCHAR, max_length=32)

            index_params = milvus_client.prepare_index_params()
            index_params.add_index(
                field_name="embedding",
                index_type="IVF_FLAT",
                metric_type=MILVUS_CONFIG["metric_type"],
                params={"nlist": 128}
            )

            milvus_client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )
            print(f"Milvus集合 '{collection_name}' 创建成功")
        else:
            print(f"Milvus集合 '{collection_name}' 已存在")

        return True
    except Exception as e:
        print(f"Milvus初始化失败: {e}")
        return False

def get_embedding(text: str) -> list:
    """生成文本向量嵌入 - 和原来一样"""
    if EMBEDDING_AVAILABLE and EMBEDDING_MODEL:
        embedding = EMBEDDING_MODEL.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    else:
        return np.random.randn(MILVUS_CONFIG["dim"]).tolist()

# 初始化Milvus
init_milvus()