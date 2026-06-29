# config/app_config.py 
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
from pydantic import BaseModel
from typing import Optional, Any

# 文件上传目录
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 解析任务并发控制
MAX_CONCURRENT_PARSING = 3
parsing_semaphore = threading.Semaphore(MAX_CONCURRENT_PARSING)
executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_PARSING)

# Token存储
active_tokens: dict = {}

# 通用响应模型
class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None

def log_operation(user_id: int, operation_type: str, detail: str, 
                  kb_id: int = None, doc_id: int = None, status: str = "success"):
    """记录操作日志"""
    import json
    from config.database import get_db
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                detail_json = json.dumps({"message": detail, "status": status}, ensure_ascii=False)
                cursor.execute("""
                    INSERT INTO operation_logs (user_id, operation_type, kb_id, doc_id, detail, ip_address, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (user_id, operation_type, kb_id, doc_id, detail_json, "127.0.0.1"))
    except Exception as e:
        print(f"记录操作日志失败: {e}")