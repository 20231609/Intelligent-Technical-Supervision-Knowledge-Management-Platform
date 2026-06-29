# controller/search_controller.py
"""搜索控制器"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from service import search_service
from config.app_config import ResponseModel

router = APIRouter(prefix="/api/search", tags=["搜索"])

class SearchMode(str, Enum):
    SEMANTIC = "semantic"
    SEMANTIC_RERANK = "semantic_rerank"

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="检索查询")
    kb_ids: Optional[List[int]] = Field(None, description="知识库ID列表")
    search_mode: SearchMode = SearchMode.SEMANTIC_RERANK
    top_k: Optional[int] = Field(10, ge=1, le=50)
    similarity_threshold: Optional[float] = Field(0.7, ge=0, le=1)
    tag_filters: Optional[List[str]] = Field(None, description="标签过滤")
    rerank_top_n: Optional[int] = Field(5, ge=1, le=20)

@router.post("", response_model=ResponseModel)
async def search_knowledge(request: SearchRequest):
    """知识检索"""
    try:
        result = search_service.search_knowledge_service(
            query=request.query,
            kb_ids=request.kb_ids,
            search_mode=request.search_mode.value,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            tag_filters=request.tag_filters,
            rerank_top_n=request.rerank_top_n
        )
        return ResponseModel(code=200, message="success", data=result)
    except Exception as e:
        return ResponseModel(code=500, message=f"检索失败: {str(e)}")