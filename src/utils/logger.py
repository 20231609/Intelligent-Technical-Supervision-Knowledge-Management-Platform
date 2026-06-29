import logging

# 日志配置。
# 规约要求日志级别包含 INFO、WARN、ERROR，并使用 [traceId] [userId] message 格式。
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("knowledge_base_rag")


def buildLogMessage(traceId: str, userId: str, message: str) -> str:
    """构造统一日志格式，便于根据 traceId 追踪一次请求。"""
    return f"[{traceId}] [{userId}] {message}"
