# controller/system_controller.py
"""系统控制器"""
from fastapi import APIRouter, Query
from service import auth_service, milvus_service
from config.app_config import ResponseModel
from config.milvus_config import MILVUS_AVAILABLE, milvus_client, MILVUS_CONFIG, EMBEDDING_AVAILABLE, EMBEDDING_DIM
from datetime import datetime

router = APIRouter(prefix="/api", tags=["系统"])

@router.get("/health", response_model=ResponseModel)
async def health_check():
    """健康检查"""
    return ResponseModel(code=200, message="服务器运行正常", data={
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.3.0",
        "milvus_connected": MILVUS_AVAILABLE and milvus_client is not None,
        "embedding_available": EMBEDDING_AVAILABLE,
        "embedding_dim": EMBEDDING_DIM
    })

@router.get("/milvus/status", response_model=ResponseModel)
async def get_milvus_status(token: str = Query(..., description="认证Token")):
    """Milvus状态"""
    try:
        auth_service.require_admin_service(token)
        status = milvus_service.get_milvus_status()
        return ResponseModel(code=200, message="success", data=status)
    except ValueError as e:
        return ResponseModel(code=403, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"查询失败: {str(e)}")

@router.post("/milvus/rebuild", response_model=ResponseModel)
async def rebuild_milvus_index(token: str = Query(..., description="认证Token")):
    """重建Milvus索引"""
    try:
        auth_service.require_admin_service(token)
        inserted = milvus_service.rebuild_milvus_index()
        return ResponseModel(code=200, message=f"重建成功，导入{inserted}条向量", data={"inserted_count": inserted})
    except ValueError as e:
        return ResponseModel(code=403, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=f"重建失败: {str(e)}")