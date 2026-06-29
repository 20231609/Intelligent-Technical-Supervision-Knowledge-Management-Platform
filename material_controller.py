# controller/material_controller.py
"""素材控制器"""
from fastapi import APIRouter, Query, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional
from service import material_service, auth_service
from config.app_config import ResponseModel

router = APIRouter(prefix="/api/materials", tags=["素材"])

@router.get("", response_model=ResponseModel)
async def list_materials(
    type: Optional[str] = Query(None, description="类型过滤"),
    keyword: Optional[str] = Query(None, description="名称搜索"),
    tag_filters: Optional[str] = Query(None, description="标签过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    token: str = Query(..., description="认证Token")
):
    """素材列表 - 已有分页支持"""
    try:
        auth_service.verify_token_service(token)
        result = material_service.list_materials_service(type, keyword, page, page_size)
        return ResponseModel(code=200, message="success", data=result)
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"查询失败: {str(e)}")

@router.post("/upload", response_model=ResponseModel)
async def upload_material(
    file: UploadFile = File(...),
    name: str = Form(...),
    type: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    token: str = Form(..., description="认证Token")
):
    """上传素材"""
    try:
        user = auth_service.verify_token_service(token)
        material_id = material_service.upload_material_service(
            file, name, type, description, tags, user["id"]
        )
        return ResponseModel(code=200, message="上传成功", data={"id": material_id})
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"上传失败: {str(e)}")

@router.put("/{material_id}/tags", response_model=ResponseModel)
async def update_material_tags(
    material_id: int,
    request: dict,
    token: str = Query(..., description="认证Token")
):
    """编辑素材标签"""
    try:
        user = auth_service.verify_token_service(token)
        material_service.update_material_tags_service(material_id, request, user["id"])
        return ResponseModel(code=200, message="标签更新成功", data={"id": material_id, "tags": request})
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"更新失败: {str(e)}")

@router.delete("/{material_id}", response_model=ResponseModel)
async def delete_material(material_id: int, token: str = Query(..., description="认证Token")):
    """删除素材"""
    try:
        user = auth_service.verify_token_service(token)
        material_service.delete_material_service(material_id, user["id"])
        return ResponseModel(code=200, message="删除成功")
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"删除失败: {str(e)}")