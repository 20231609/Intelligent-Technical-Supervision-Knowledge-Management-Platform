import asyncio
import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.config.database import SessionLocal, getDbSession
from src.entity.knowledge_base_entity import ChatSession
from src.service.qa_service import (
    CONFIG,
    classifyIntent,
    createDocument,
    ensureSession,
    generateAnswer,
    getStats,
    listSessions,
    retrieveKnowledge,
    saveChatMessage,
)
from src.utils.auth import loginUser, registerUser, requireAdmin, verifyCurrentUser
from src.utils.response import buildSuccessResponse
from src.vo.knowledge_base_vo import (
    ChatRequest,
    DocumentCreateRequest,
    KnowledgeSearchRequest,
    LoginRequest,
    RegisterRequest,
)

router = APIRouter(prefix="/api")


def _question(request: ChatRequest) -> str:
    value = (request.content or request.message or request.question or "").strip()
    if not value:
        raise HTTPException(status_code=400, detail="问题不能为空")
    return value


def _sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/login")
def login(request: LoginRequest):
    return loginUser(request.username, request.password)


@router.post("/register", status_code=201)
def register(request: RegisterRequest):
    return registerUser(request.username, request.password)


@router.get("/me")
def me(currentUser: dict = Depends(verifyCurrentUser)):
    return currentUser


@router.post("/knowledge-base/documents")
def createKnowledgeDocument(
    request: DocumentCreateRequest,
    db: Session = Depends(getDbSession),
    currentUser: dict = Depends(verifyCurrentUser),
):
    data = createDocument(db, currentUser, request.title, request.content, request.knowledgeBaseId)
    return buildSuccessResponse(data)


@router.post("/knowledge-base/search")
@router.post("/search")
def searchKnowledge(
    request: KnowledgeSearchRequest,
    db: Session = Depends(getDbSession),
    currentUser: dict = Depends(verifyCurrentUser),
):
    data = retrieveKnowledge(db, request.query, request.topK, request.similarityThreshold, request.knowledgeBaseIds)
    return buildSuccessResponse({"query": request.query, "results": data})


@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(getDbSession),
    currentUser: dict = Depends(verifyCurrentUser),
):
    question = _question(request)
    intent = classifyIntent(question)
    docs = retrieveKnowledge(db, question, int(CONFIG["topK"]), float(CONFIG["similarityThreshold"]))
    answer, usedFallback = generateAnswer(question, request.history, docs, intent)
    session = ensureSession(db, currentUser, request.session_id or request.sessionId, question[:30])
    messageId = saveChatMessage(db, currentUser, session.id, question, answer, docs)
    return {
        "messageId": messageId,
        "session_id": session.id,
        "sessionId": session.id,
        "answer": answer,
        "content": answer,
        "intent": intent["intent"],
        "route": intent["route"],
        "sources": docs,
        "citations": docs,
        "used_fallback": usedFallback,
    }


@router.post("/chat/stream")
async def chatStream(
    request: ChatRequest,
    db: Session = Depends(getDbSession),
    currentUser: dict = Depends(verifyCurrentUser),
):
    question = _question(request)
    session = ensureSession(db, currentUser, request.session_id or request.sessionId, question[:30])
    sessionId = session.id
    messageId = request.messageId or uuid4().hex

    async def generate():
        try:
            yield _sse(
                "thinking",
                {
                    "messageId": messageId,
                    "sessionId": sessionId,
                    "stepId": "intent",
                    "label": "意图识别",
                    "status": "running",
                    "detail": "正在识别用户问题类型",
                },
            )
            await asyncio.sleep(0.05)
            intent = classifyIntent(question)
            yield _sse(
                "thinking",
                {
                    "messageId": messageId,
                    "sessionId": sessionId,
                    "stepId": "intent",
                    "label": "意图识别",
                    "status": "done",
                    "detail": f"识别为 {intent['intent']}，路由到 {intent['route']}",
                },
            )
            yield _sse(
                "thinking",
                {
                    "messageId": messageId,
                    "sessionId": sessionId,
                    "stepId": "retrieval",
                    "label": "知识检索",
                    "status": "running",
                    "detail": "正在检索知识库片段",
                },
            )
            docs = retrieveKnowledge(db, question, int(CONFIG["topK"]), float(CONFIG["similarityThreshold"]))
            for index, doc in enumerate(docs, start=1):
                yield _sse(
                    "citation",
                    {
                        "messageId": messageId,
                        "sessionId": sessionId,
                        "citation": {
                            "id": doc["chunkId"],
                            "documentId": doc["documentId"],
                            "documentName": doc["documentName"],
                            "snippet": doc["snippet"],
                            "relevanceScore": doc["score"],
                            "markerIndex": index,
                        },
                    },
                )
            yield _sse(
                "thinking",
                {
                    "messageId": messageId,
                    "sessionId": sessionId,
                    "stepId": "retrieval",
                    "label": "知识检索",
                    "status": "done",
                    "detail": f"召回 {len(docs)} 条相关片段",
                },
            )
            yield _sse(
                "thinking",
                {
                    "messageId": messageId,
                    "sessionId": sessionId,
                    "stepId": "answer",
                    "label": "回答生成",
                    "status": "running",
                    "detail": "正在调用 DeepSeek 生成回答",
                },
            )
            answer, _ = generateAnswer(question, request.history, docs, intent)
            for token in answer:
                yield _sse("token", {"messageId": messageId, "sessionId": sessionId, "content": token})
                await asyncio.sleep(0.001)
            streamDb = SessionLocal()
            try:
                saveChatMessage(streamDb, currentUser, sessionId, question, answer, docs)
            finally:
                streamDb.close()
            yield _sse(
                "thinking",
                {
                    "messageId": messageId,
                    "sessionId": sessionId,
                    "stepId": "answer",
                    "label": "回答生成",
                    "status": "done",
                    "detail": "回答生成完成",
                },
            )
            yield _sse("done", {"messageId": messageId, "sessionId": sessionId})
        except Exception as error:
            yield _sse("error", {"messageId": messageId, "sessionId": sessionId, "message": str(error)})

    return StreamingResponse(generate(), media_type="text/event-stream; charset=utf-8")


@router.post("/session/create")
@router.post("/sessions")
def createSession(db: Session = Depends(getDbSession), currentUser: dict = Depends(verifyCurrentUser)):
    session = ensureSession(db, currentUser, None)
    return {"id": session.id, "session_id": session.id, "sessionId": session.id, "title": session.title}


@router.get("/session/list")
@router.get("/sessions")
def getSessions(db: Session = Depends(getDbSession), currentUser: dict = Depends(verifyCurrentUser)):
    return {"sessions": listSessions(db, currentUser)}


@router.delete("/session/{sessionId}")
@router.delete("/sessions/{sessionId}")
def deleteSession(sessionId: str, db: Session = Depends(getDbSession), currentUser: dict = Depends(verifyCurrentUser)):
    session = db.query(ChatSession).filter_by(id=sessionId, user_id=currentUser["userId"], deleted_flag=0).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    session.deleted_flag = 1
    db.commit()
    return {"message": "会话已删除"}


@router.get("/admin/qa-config")
def getQaConfig(currentUser: dict = Depends(verifyCurrentUser)):
    requireAdmin(currentUser)
    return buildSuccessResponse(CONFIG)


@router.put("/admin/qa-config")
def updateQaConfig(payload: dict, currentUser: dict = Depends(verifyCurrentUser)):
    requireAdmin(currentUser)
    CONFIG.update({key: value for key, value in payload.items() if value is not None})
    return buildSuccessResponse(CONFIG)


@router.get("/admin/stats")
def stats(db: Session = Depends(getDbSession), currentUser: dict = Depends(verifyCurrentUser)):
    requireAdmin(currentUser)
    return buildSuccessResponse(getStats(db))


@router.get("/health")
def health():
    return {"status": "ok"}
