from fastapi import FastAPI
from app.core.config import settings
from app.core.error_handler import app_exception_handler
app = FastAPI(title=settings.app_name, version=settings.app_version)
# 注册全局异常处理
app.add_exception_handler(Exception, app_exception_handler)
@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version
    }