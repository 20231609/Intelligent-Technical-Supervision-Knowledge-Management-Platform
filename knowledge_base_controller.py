# controller/knowledge_base_controller.py
"""知识库控制器"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from service import knowledge_base_service
from service import auth_service
from config.app_config import ResponseModel

router = APIRouter(prefix="/api/knowledge-bases", tags=["知识库"])

class KBType(str, Enum):
    REGULATION = "regulation"
    TECH_REPORT = "tech_report"
    TERM_ENTRY = "term_entry"
    GENERAL = "general"

class SegmentStrategy(BaseModel):
    type: str = Field("heading", pattern="^(heading|fixed)$")
    chunk_size: Optional[int] = Field(500, ge=100, le=2000)
    overlap: Optional[int] = Field(50, ge=0, le=500)
    separator: Optional[str] = "\n"
    recursive_merge: Optional[bool] = True

class SearchStrategy(BaseModel):
    type: str = Field("semantic", pattern="^(semantic|semantic_rerank)$")
    top_k: Optional[int] = Field(10, ge=1, le=100)
    similarity_threshold: Optional[float] = Field(0.7, ge=0, le=1)
    rerank_threshold: Optional[float] = Field(0.5, ge=0, le=1)

class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = ""
    type: KBType = KBType.GENERAL
    segment_strategy: SegmentStrategy = SegmentStrategy()
    search_strategy: SearchStrategy = SearchStrategy()

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    segment_strategy: Optional[SegmentStrategy] = None
    search_strategy: Optional[SearchStrategy] = None

@router.get("", response_model=ResponseModel)
async def list_knowledge_bases(
    type: Optional[str] = Query(None, description="类型过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    token: str = Query(..., description="认证Token")
):
    """知识库列表 - 支持类型过滤、关键词搜索、分页"""
    try:
        auth_service.verify_token_service(token)
        result = knowledge_base_service.list_knowledge_bases_service(type, keyword, page, page_size)
        return ResponseModel(code=200, message="success", data=result)
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"查询失败: {str(e)}")

@router.post("", response_model=ResponseModel)
async def create_knowledge_base(
    request: KnowledgeBaseCreate,
    token: str = Query(..., description="认证Token")
):
    """创建知识库"""
    try:
        user = auth_service.verify_token_service(token)
        kb_id = knowledge_base_service.create_knowledge_base_service(
            request.name, request.description, request.type.value,
            request.segment_strategy.dict(), request.search_strategy.dict(),
            user["id"]
        )
        return ResponseModel(code=200, message="创建成功", data={"id": kb_id})
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"创建失败: {str(e)}")

@router.get("/{kb_id}", response_model=ResponseModel)
async def get_knowledge_base(kb_id: int, token: str = Query(..., description="认证Token")):
    """知识库详情 - 新增接口，前端需要"""
    try:
        auth_service.verify_token_service(token)
        kb = knowledge_base_service.get_knowledge_base_detail(kb_id)
        if not kb:
            return ResponseModel(code=404, message="知识库不存在")
        return ResponseModel(code=200, message="success", data=kb)
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"查询失败: {str(e)}")

@router.put("/{kb_id}", response_model=ResponseModel)
async def update_knowledge_base(
    kb_id: int,
    request: KnowledgeBaseUpdate,
    token: str = Query(..., description="认证Token")
):
    """编辑知识库 - 策略变更自动触发重处理"""
    try:
        user = auth_service.verify_token_service(token)
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        if request.segment_strategy is not None:
            updates["segment_strategy"] = request.segment_strategy.dict()
        if request.search_strategy is not None:
            updates["search_strategy"] = request.search_strategy.dict()

        if not updates:
            return ResponseModel(code=400, message="没有需要更新的字段")

        strategy_changed, reprocess_count = knowledge_base_service.update_knowledge_base_service(
            kb_id, updates, user["id"]
        )
        
        if strategy_changed is None:
            return ResponseModel(code=404, message=reprocess_count)

        msg = "更新成功"
        if strategy_changed:
            msg += f"，已触发{reprocess_count}个文档重新处理"

        return ResponseModel(code=200, message=msg, data={
            "id": kb_id, "strategy_changed": strategy_changed
        })
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"更新失败: {str(e)}")

@router.delete("/{kb_id}", response_model=ResponseModel)
async def delete_knowledge_base(kb_id: int, token: str = Query(..., description="认证Token")):
    """删除知识库"""
    try:
        user = auth_service.verify_token_service(token)
        knowledge_base_service.delete_knowledge_base_service(kb_id, user["id"])
        return ResponseModel(code=200, message="删除成功")
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"删除失败: {str(e)}")

@router.post("/batch-delete", response_model=ResponseModel)
async def batch_delete_knowledge_bases(
    request: dict,
    token: str = Query(..., description="认证Token")
):
    """批量删除知识库"""
    try:
        user = auth_service.verify_token_service(token)
        ids = request.get("ids", [])
        if not ids:
            return ResponseModel(code=400, message="请选择要删除的知识库")
        count = knowledge_base_service.batch_delete_knowledge_bases_service(ids, user["id"])
        return ResponseModel(code=200, message=f"成功删除{count}个知识库", data={"deleted_count": count})
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"删除失败: {str(e)}")