from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class DocumentCreateRequest(BaseModel):
    title: str
    content: str
    knowledgeBaseId: str = "default"


class KnowledgeSearchRequest(BaseModel):
    query: str
    topK: int | None = None
    similarityThreshold: float | None = None
    knowledgeBaseIds: list[str] | None = None


class ChatRequest(BaseModel):
    question: str | None = None
    message: str | None = None
    content: str | None = None
    session_id: str | None = None
    sessionId: str | None = None
    messageId: str | None = None
    history: list[dict] | None = None
