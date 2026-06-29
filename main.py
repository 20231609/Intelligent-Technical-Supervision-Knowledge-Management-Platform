# main.py
"""AI NEXUS 知识管理API v3.3 - 分层架构版"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controller import auth_controller, knowledge_base_controller, document_controller
from controller import search_controller, material_controller, system_controller

app = FastAPI(
    title="AI NEXUS - 知识管理API v3.3",
    description="电力行业知识管理系统后端接口 - 分层架构版",
    version="3.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_controller.router)
app.include_router(knowledge_base_controller.router)
app.include_router(document_controller.router)
app.include_router(search_controller.router)
app.include_router(material_controller.router)
app.include_router(system_controller.router)


def get_admin_token():
    """直接获取admin用户的token（仅用于调试）"""
    from service import auth_service
    result, error = auth_service.login_service(username="admin", password="admin123")
    if result:
        print(f"\n{'=' * 50}")
        print(f"Admin Token: {result['token']}")
        print(f"{'=' * 50}\n")
        return result['token']
    else:
        print(f"获取失败: {error}")
        return None


if __name__ == "__main__":
    import socket
    import uvicorn
    from config.database import DB_CONFIG
    from config.milvus_config import MILVUS_CONFIG, EMBEDDING_AVAILABLE, EMBEDDING_DIM


    def find_free_port(start_port: int = 8000, max_attempts: int = 20) -> int:
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind(("0.0.0.0", port))
                    return port
                except OSError:
                    continue
        raise RuntimeError(f"无法找到可用端口（从 {start_port} 开始）")


    port = find_free_port()

    print("=" * 70)
    print("AI NEXUS 知识管理API v3.3 (分层架构版)")
    print("=" * 70)
    print(f"MySQL数据库: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"Milvus向量库: 本地文件模式 (./milvus_knowledge.db)")
    print(f"向量维度: {MILVUS_CONFIG['dim']}")
    print(f"嵌入模型: {'sentence-transformers' if EMBEDDING_AVAILABLE else 'random(fallback)'}")
    print("=" * 70)
    print(f"服务地址: http://localhost:{port}")
    print(f"API文档:  http://localhost:{port}/docs")
    print("=" * 70)

    # 在服务启动前获取 admin token
    admin_token = get_admin_token()

    uvicorn.run(app, host="0.0.0.0", port=port)