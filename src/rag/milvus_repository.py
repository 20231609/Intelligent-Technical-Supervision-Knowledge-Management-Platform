from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from src.config.settings import settings


def connectMilvus() -> None:
    connections.connect(alias="default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)


def createMilvusCollection() -> Collection:
    connectMilvus()
    if utility.has_collection(settings.MILVUS_COLLECTION):
        collection = Collection(settings.MILVUS_COLLECTION)
    else:
        schema = CollectionSchema(
            fields=[
                FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
                FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="knowledge_base_id", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.EMBEDDING_DIM),
            ],
            description="Knowledge base chunk vectors",
        )
        collection = Collection(settings.MILVUS_COLLECTION, schema=schema)

    if not collection.has_index():
        collection.create_index(
            "embedding",
            {"index_type": "AUTOINDEX", "metric_type": "COSINE", "params": {}},
        )
    collection.load()
    return collection


def upsertVectors(rows: list[dict]) -> None:
    if not rows:
        return
    collection = createMilvusCollection()
    collection.upsert(
        [
            [row["chunk_id"] for row in rows],
            [row["user_id"] for row in rows],
            [row["knowledge_base_id"] for row in rows],
            [row["document_id"] for row in rows],
            [row["embedding"] for row in rows],
        ]
    )
    collection.flush()


def searchVectors(queryEmbedding: list[float], topK: int, knowledgeBaseIds: list[str] | None = None) -> list[dict]:
    collection = createMilvusCollection()
    expr = None
    if knowledgeBaseIds:
        quoted = ", ".join(f'"{item}"' for item in knowledgeBaseIds)
        expr = f"knowledge_base_id in [{quoted}]"

    results = collection.search(
        data=[queryEmbedding],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {}},
        limit=topK,
        expr=expr,
        output_fields=["chunk_id", "document_id", "knowledge_base_id"],
    )
    hits: list[dict] = []
    for hit in results[0]:
        hits.append(
            {
                "chunk_id": hit.entity.get("chunk_id"),
                "document_id": hit.entity.get("document_id"),
                "knowledge_base_id": hit.entity.get("knowledge_base_id"),
                "score": float(hit.score),
            }
        )
    return hits
