# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.error_handler import app_exception_handler
from api.routes.artifact import router as artifact_router
from api.routes import task

app = FastAPI(title=settings.app_name, version=settings.app_version)

# 配置 CORS (允许前端跨域调用)
# 这是前后端分离开发必须的，否则前端 fetch 会报 CORS 错误
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许哪些源访问，开发环境允许所有，生产环境建议改为 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理
app.add_exception_handler(Exception, app_exception_handler)

# 注册路由
# 前端代码 API_BASE = "http://localhost:8000/api"
# 所以我们需要加上 prefix="/api"
app.include_router(task.router, prefix="/api", tags=["Task"])
app.include_router(artifact_router, prefix="/api", tags=["Artifact"])

@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version
    }