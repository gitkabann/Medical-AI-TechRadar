# app/core/error_handler.py

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from app.core.logger import get_logger
from app.models.error import ErrorResponse

logger = get_logger("ErrorHandler")

# ==========================================
# 1. 面向 Workers 的故障分析器 (新增)
# ==========================================
class WorkerErrorHandler:
    """
    专门处理后台 Agent 的异常
    返回决策建议：RETRY (重试) / SKIP (跳过/丢弃) / ABORT (严重故障)
    """
    @staticmethod
    def analyze(e: Exception, component: str, task_id: str = None) -> str:
        err_msg = str(e)
        err_type = type(e).__name__
        
        # 定义决策上下文日志
        log_ctx = {
            "component": component,
            "error_type": err_type,
            "task_id": task_id
        }

        # A. 网络/瞬态错误 -> 建议重试 (RETRY)
        # 配合 Redis Pending 机制，不 ACK 消息，等待超时重新投递
        if "ConnectionError" in err_type or "Timeout" in err_msg or "429" in err_msg:
            logger.warning("Transient network error (Will Retry)", **log_ctx, suggestion="RETRY")
            return "RETRY"

        # B. 数据/逻辑错误 -> 建议跳过 (SKIP)
        # 这种错误重试一万次也是挂，必须 ACK 掉以防死循环
        if "KeyError" in err_type or "ValueError" in err_type or "SyntaxError" in err_msg:
            logger.error("Logic/Data error (Skip Task)", **log_ctx, suggestion="SKIP")
            return "SKIP"
            
        # C. 熔断/策略拦截 -> 建议跳过 (SKIP)
        if "Max steps exceeded" in err_msg:
             logger.error("Circuit Breaker Triggered", **log_ctx, suggestion="SKIP")
             return "SKIP"

        # D. 基础设施严重错误 -> 建议中止 (ABORT)
        # 比如 Redis 挂了，Mongo 挂了，这时候 Worker 应该自杀重启
        if "Redis" in err_type or "Mongo" in err_type:
            logger.critical("🚨 INFRASTRUCTURE FAILURE", **log_ctx, alert=True)
            return "ABORT"

        # E. 未知错误 -> 默认记录并跳过 (防止阻塞队列)
        logger.error(f"Unhandled Worker Exception: {err_msg}", **log_ctx, exc_info=True)
        return "SKIP"

# 全局单例供 Worker 使用
worker_error_handler = WorkerErrorHandler()


# ==========================================
# 2. 面向 API 的异常处理器 (保留并优化)
# ==========================================
async def app_exception_handler(request: Request, exc: Exception):
    """
    FastAPI 全局异常捕获
    """
    # 获取请求的 trace_id (如果有的话，通常在 header 里)
    trace_id = request.headers.get("X-Trace-Id", "unknown")

    logger.error(f"[API ERROR] {exc!r}", task_id=trace_id, path=request.url.path)

    err = ErrorResponse(
        code="INTERNAL_ERROR",
        message="服务器发生未知错误，请稍后再试。",
        hint=str(exc)[:200]  # 只截取错误前 200 字
    )

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=err.model_dump()
    )