# controller/document_controller.py
"""文档控制器 - 新增编辑标签、重试、批量删除接口"""
from fastapi import APIRouter, Query, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List
from service import document_service, auth_service
from config.app_config import ResponseModel

router = APIRouter(prefix="/api/documents", tags=["文档"])

class UpdateTagsRequest(BaseModel):
    """编辑文档标签请求"""
    tags: List[str] = Field(..., description="标签列表")

class BatchDeleteRequest(BaseModel):
    """批量删除文档请求"""
    ids: List[int] = Field(..., description="文档ID列表")

@router.get("", response_model=ResponseModel)
async def list_documents(
    kb_id: int = Query(..., description="知识库ID"),
    status: Optional[str] = Query(None, description="状态过滤"),
    keyword: Optional[str] = Query(None, description="文件名搜索"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    token: str = Query(..., description="认证Token")
):
    """文档列表"""
    try:
        auth_service.verify_token_service(token)
        result = document_service.list_documents_service(kb_id, status, keyword, page, page_size)
        return ResponseModel(code=200, message="success", data=result)
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"查询失败: {str(e)}")

@router.post("/upload", response_model=ResponseModel)
async def upload_document(
    file: UploadFile = File(..., description="上传文件"),
    kb_id: int = Form(..., description="知识库ID"),
    tags: Optional[str] = Form("", description="标签，逗号分隔"),
    token: str = Form(..., description="认证Token")
):
    """上传文档"""
    try:
        user = auth_service.verify_token_service(token)
        result = document_service.upload_document_service(file, kb_id, tags, user["id"])
        return ResponseModel(code=200, message="上传成功，开始处理", data=result)
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"上传失败: {str(e)}")

# ========== 新增接口：编辑文档标签 ==========
@router.put("/{doc_id}/tags", response_model=ResponseModel)
async def update_document_tags(
    doc_id: int,
    request: UpdateTagsRequest,
    token: str = Query(..., description="认证Token")
):
    """编辑文档标签 - 新增接口"""
    try:
        user = auth_service.verify_token_service(token)
        document_service.update_document_tags_service(doc_id, request.tags, user["id"])
        return ResponseModel(code=200, message="标签更新成功", data={
            "id": doc_id, 
            "tags": request.tags
        })
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"更新失败: {str(e)}")

# ========== 新增接口：重试文档处理 ==========
@router.post("/{doc_id}/retry", response_model=ResponseModel)
async def retry_document(
    doc_id: int,
    token: str = Query(..., description="认证Token")
):
    """重试文档处理 - 新增接口"""
    try:
        user = auth_service.verify_token_service(token)
        document_service.retry_document_service(doc_id, user["id"])
        return ResponseModel(code=200, message="已触发重新处理", data={"id": doc_id, "status": "uploaded"})
    except ValueError as e:
        return ResponseModel(code=400, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"重试失败: {str(e)}")

# ========== 新增接口：批量删除文档 ==========
@router.post("/batch-delete", response_model=ResponseModel)
async def batch_delete_documents(
    request: BatchDeleteRequest,
    token: str = Query(..., description="认证Token")
):
    """批量删除文档 - 新增接口"""
    try:
        user = auth_service.verify_token_service(token)
        if not request.ids:
            return ResponseModel(code=400, message="请选择要删除的文档")
        count = document_service.batch_delete_documents_service(request.ids, user["id"])
        return ResponseModel(code=200, message=f"成功删除{count}个文档", data={"deleted_count": count})
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"删除失败: {str(e)}")

@router.get("/{doc_id}/chunks", response_model=ResponseModel)
async def get_document_chunks(
    doc_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    keyword: Optional[str] = Query(None, description="切片内容搜索"),
    token: str = Query(..., description="认证Token")
):
    """查看切片详情"""
    try:
        auth_service.verify_token_service(token)
        result = document_service.get_document_chunks_service(doc_id, keyword, page, page_size)
        return ResponseModel(code=200, message="success", data=result)
    except ValueError as e:
        return ResponseModel(code=400, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"查询失败: {str(e)}")

# ========== 新增接口：文档状态日志查看 ==========
@router.get("/{doc_id}/status-logs", response_model=ResponseModel)
async def get_document_status_logs(
    doc_id: int,
    token: str = Query(..., description="认证Token")
):
    """获取文档处理状态变更日志 - 新增接口"""
    try:
        auth_service.verify_token_service(token)
        logs = document_service.get_document_status_logs_service(doc_id)
        return ResponseModel(code=200, message="success", data={"doc_id": doc_id, "logs": logs})
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"查询失败: {str(e)}")