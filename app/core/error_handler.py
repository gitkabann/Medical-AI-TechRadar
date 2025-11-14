from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from app.core.logger import get_logger
from app.models.error import AppError

logger = get_logger(__name__)


async def app_exception_handler(request: Request, exc: Exception):
    """全局异常捕获：所有未处理的错误都会走这里"""

    logger.error(f"[UNHANDLED ERROR] {exc!r}")

    err = AppError(
        code="INTERNAL_ERROR",
        message="服务器发生未知错误，请稍后再试。",
        hint=str(exc)[:200]  # 只截取错误前 200 字
    )

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=err.model_dump()
    )
