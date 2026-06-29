from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from src.config.database import Base, engine
from src.controller.api_controller import router as apiRouter
from src.entity import knowledge_base_entity  # noqa: F401
from src.rag.milvus_repository import createMilvusCollection
from src.utils.response import buildErrorResponse

app = FastAPI(title="Intelligent QA System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apiRouter)

ROOT_DIR = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT_DIR / "dist"
ASSETS_DIR = DIST_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    createMilvusCollection()


@app.exception_handler(HTTPException)
def handleHttpException(request: Request, exception: HTTPException):
    return JSONResponse(
        status_code=exception.status_code,
        content=buildErrorResponse(exception.status_code, str(exception.detail)),
    )


@app.exception_handler(Exception)
def handleException(request: Request, exception: Exception):
    return JSONResponse(status_code=500, content=buildErrorResponse(500, "服务端错误，请稍后重试"))


@app.get("/")
def index():
    indexPath = DIST_DIR / "index.html"
    if indexPath.exists():
        return FileResponse(indexPath)
    return {"service": "Intelligent QA System", "docs": "/docs"}


@app.get("/{path:path}")
def spa(path: str):
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="接口不存在")
    indexPath = DIST_DIR / "index.html"
    if indexPath.exists():
        return FileResponse(indexPath)
    raise HTTPException(status_code=404, detail="资源不存在")
