import json
from datetime import datetime, timedelta
from uuid import uuid4

import requests
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.entity.knowledge_base_entity import ChatMessage, ChatSession, KnowledgeBaseChunk, KnowledgeBaseDocument
from src.rag.embedding_client import generateEmbedding
from src.rag.milvus_repository import searchVectors, upsertVectors
from src.rag.text_splitter import splitText


CONFIG = {
    "termKnowledgeBaseIds": ["terms"],
    "technicalKnowledgeBaseIds": ["default"],
    "topK": settings.DEFAULT_TOP_K,
    "similarityThreshold": settings.DEFAULT_SIMILARITY_THRESHOLD,
    "rerankThreshold": settings.DEFAULT_RERANK_THRESHOLD,
    "llmApiUrl": f"{settings.OPENAI_BASE_URL}/chat/completions",
    "llmModelName": settings.LLM_MODEL,
    "llmTimeoutSeconds": settings.LLM_TIMEOUT_SECONDS,
}


def classifyIntent(question: str) -> dict:
    keywords = ("SCR", "脱硝", "电力", "设备", "系统", "规程", "故障", "启动", "NOx", "氮氧化物", "知识库")
    if any(keyword.lower() in question.lower() for keyword in keywords):
        return {"intent": "knowledge_qa", "route": "rag_knowledge_answer"}
    if any(keyword in question for keyword in ("你好", "您好", "天气", "介绍", "闲聊")):
        return {"intent": "general_chat", "route": "general_llm_chat"}
    return {"intent": "knowledge_qa", "route": "rag_knowledge_answer"}


def createDocument(db: Session, currentUser: dict, title: str, content: str, knowledgeBaseId: str = "default") -> dict:
    if not title.strip() or not content.strip():
        raise ValueError("标题和内容不能为空")

    documentId = uuid4().hex
    chunks = splitText(content)
    document = KnowledgeBaseDocument(
        id=documentId,
        user_id=currentUser["userId"],
        knowledge_base_id=knowledgeBaseId,
        title=title.strip(),
        source_type="manual",
        status="ready",
        chunk_count=len(chunks),
    )
    db.add(document)

    vectorRows: list[dict] = []
    for index, chunkText in enumerate(chunks):
        chunkId = uuid4().hex
        chunk = KnowledgeBaseChunk(
            id=chunkId,
            user_id=currentUser["userId"],
            knowledge_base_id=knowledgeBaseId,
            document_id=documentId,
            chunk_index=index,
            content=chunkText,
            token_count=len(chunkText),
            milvus_collection=settings.MILVUS_COLLECTION,
        )
        db.add(chunk)
        vectorRows.append(
            {
                "chunk_id": chunkId,
                "user_id": currentUser["userId"],
                "knowledge_base_id": knowledgeBaseId,
                "document_id": documentId,
                "embedding": generateEmbedding(chunkText),
            }
        )

    db.commit()
    upsertVectors(vectorRows)
    return {"documentId": documentId, "title": document.title, "chunkCount": len(chunks), "status": "ready"}


def retrieveKnowledge(
    db: Session,
    query: str,
    topK: int | None = None,
    similarityThreshold: float | None = None,
    knowledgeBaseIds: list[str] | None = None,
) -> list[dict]:
    topK = topK or int(CONFIG["topK"])
    threshold = settings.DEFAULT_SIMILARITY_THRESHOLD if similarityThreshold is None else similarityThreshold
    hits = searchVectors(generateEmbedding(query), topK, knowledgeBaseIds)
    if not hits:
        return []

    chunkIds = [hit["chunk_id"] for hit in hits]
    chunks = db.query(KnowledgeBaseChunk).filter(KnowledgeBaseChunk.id.in_(chunkIds)).all()
    chunkMap = {chunk.id: chunk for chunk in chunks}
    docs = db.query(KnowledgeBaseDocument).filter(KnowledgeBaseDocument.id.in_([hit["document_id"] for hit in hits])).all()
    docMap = {doc.id: doc for doc in docs}

    results: list[dict] = []
    for hit in hits:
        if hit["score"] < threshold:
            continue
        chunk = chunkMap.get(hit["chunk_id"])
        doc = docMap.get(hit["document_id"])
        if not chunk or not doc:
            continue
        results.append(
            {
                "chunkId": chunk.id,
                "documentId": doc.id,
                "documentName": doc.title,
                "knowledgeBaseId": chunk.knowledge_base_id,
                "snippet": chunk.content,
                "score": hit["score"],
            }
        )
    return results


def _fallbackAnswer(question: str, intent: dict, docs: list[dict]) -> str:
    if intent["intent"] == "general_chat":
        return "你好，我是电力行业智能问答助手，可以帮助你进行知识检索、智能对话、引用溯源和运行配置测试。"
    if docs:
        bullets = "\n".join(f"- {doc['snippet'][:160]}" for doc in docs[:3])
        return f"根据知识库检索结果，整理如下：\n{bullets}\n\n建议结合现场规程和设备状态进一步核对。"
    return (
        "根据电力行业常识，SCR脱硝系统主要用于降低烟气中的 NOx 排放。"
        "启动前通常需要检查供氨压力、反应器入口烟温、稀释风机、喷氨阀门和 PLC 报警状态。"
    )


def generateAnswer(question: str, history: list[dict] | None, docs: list[dict], intent: dict) -> tuple[str, bool]:
    context = "\n".join(f"[{idx + 1}] {doc['snippet']}" for idx, doc in enumerate(docs))
    system = "你是面向电力行业的智能问答助手。回答要准确、结构清晰，并优先依据知识库片段。"
    if context:
        system += f"\n知识库片段：\n{context}"
    messages = [{"role": "system", "content": system}]
    for item in history or []:
        if item.get("role") in {"user", "assistant"} and item.get("content"):
            messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": question})

    if not settings.OPENAI_API_KEY:
        return _fallbackAnswer(question, intent, docs), True
    try:
        response = requests.post(
            f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.LLM_MODEL,
                "messages": messages,
                "temperature": 0.3,
                "stream": False,
            },
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"] or "", False
    except Exception as error:
        fallback = _fallbackAnswer(question, intent, docs)
        return f"{fallback}\n\n（DeepSeek 调用失败，已使用本地兜底回答：{error}）", True


def ensureSession(db: Session, currentUser: dict, sessionId: str | None, title: str | None = None) -> ChatSession:
    if sessionId:
        session = db.query(ChatSession).filter_by(id=sessionId, user_id=currentUser["userId"], deleted_flag=0).first()
        if session:
            return session
    session = ChatSession(id=sessionId or uuid4().hex, user_id=currentUser["userId"], title=(title or "新会话")[:255])
    db.add(session)
    db.commit()
    return session


def saveChatMessage(db: Session, currentUser: dict, sessionId: str, question: str, answer: str, docs: list[dict]) -> str:
    session = ensureSession(db, currentUser, sessionId, question[:30])
    session.title = session.title or question[:30]
    session.updated_at = datetime.utcnow()
    messageId = uuid4().hex
    db.add(
        ChatMessage(
            id=messageId,
            user_id=currentUser["userId"],
            session_id=session.id,
            question=question,
            answer=answer,
            retrieved_chunks=docs,
        )
    )
    db.commit()
    return messageId


def listSessions(db: Session, currentUser: dict) -> list[dict]:
    rows = (
        db.query(ChatSession)
        .filter_by(user_id=currentUser["userId"], deleted_flag=0)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return [
        {
            "id": item.id,
            "session_id": item.id,
            "sessionId": item.id,
            "title": item.title or "新会话",
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
        }
        for item in rows
    ]


def getStats(db: Session) -> dict:
    total = db.query(func.count(ChatMessage.id)).scalar() or 0
    start = datetime.utcnow() - timedelta(days=29)
    rows = (
        db.query(func.date(ChatMessage.created_at), func.count(ChatMessage.id))
        .filter(ChatMessage.created_at >= start)
        .group_by(func.date(ChatMessage.created_at))
        .all()
    )
    trendMap = {str(day): count for day, count in rows}
    trend = []
    for offset in range(30):
        day = (start + timedelta(days=offset)).date().isoformat()
        trend.append({"date": day, "count": int(trendMap.get(day, 0))})
    return {"totalQaCount": int(total), "last30DaysTrend": trend}


def serializeDocsForPrompt(docs: list[dict]) -> str:
    return json.dumps(docs, ensure_ascii=False)
