import asyncio
from app.core.logger import get_logger

# 获取当前模块的日志器，用于打印重试信息
logger = get_logger(__name__)

# 一个带“重试 + 超时”功能的通用异步执行工具
async def with_retry(func, retries=3, timeout=10):
    """
    带重试与超时控制的异步执行函数。
    参数:
        func: 一个异步函数（async function），不带参数或已封装参数。
        retries: 最大重试次数（默认 3 次）
        timeout: 每次执行的超时时间（秒）
    返回:
        func 执行的返回结果（如果成功）
    抛出:
        超过重试次数后仍失败的异常
    """

    # 循环尝试执行多次
    for i in range(retries):
        try:
            # asyncio.wait_for 会在超时后自动抛 TimeoutError
            return await asyncio.wait_for(func(), timeout)
        except Exception as e:
            # 捕获任何异常并打印警告日志
            logger.warning(f"Attempt {i+1} failed: {e}")

            # 如果已经到最后一次重试仍然失败，则抛出异常终止
            if i == retries - 1:
                raise