import asyncio
import random
from typing import Callable, Any, Coroutine
from contextlib import asynccontextmanager

async def with_retry(
    func: Callable[..., Coroutine[Any, Any, Any]],
    *args,
    retries: int = 3,
    timeout: float = 20.0,
    backoff: float = 1.5,
    **kwargs
):
    """
    对任意 async 函数执行：超时 + 重试 + 指数退避。
    """

    for attempt in range(1, retries + 1):
        try:
            # 带超时时间执行 func
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        except Exception as e:
            # 最后一次失败直接抛出异常
            if attempt == retries:
                raise
            # 指数退避等待后再重试.随机抖动 (random.random()) 是为了避免所有任务同时重试造成瞬时压力。
            sleep_time = backoff ** attempt + random.random()
            await asyncio.sleep(sleep_time)

class RateLimiter:
    """
    限制全局并发，例如并行最多 5 个任务。
    """
    def __init__(self, max_concurrency: int):
        self.sem = asyncio.Semaphore(max_concurrency)

    @asynccontextmanager
    async def limit(self):
        async with self.sem:
            yield