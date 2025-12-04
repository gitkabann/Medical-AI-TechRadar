import os
import random
import time
from functools import wraps

class ChaosMonkey:
    def __init__(self):
        # 默认关闭，除非显式开启
        self.enabled = os.getenv("ENABLE_CHAOS", "false").lower() == "true"#未设置或为空则默认false；转小写字母后与"true"比较
        self.failure_rate = 0.5  # 50% 概率失败

    def simulate(self, component_name: str):
        """如果命中概率，则抛出模拟异常"""
        if self.enabled and random.random() < self.failure_rate:
            error_msg = f"💥 [Chaos] 模拟故障在 {component_name}中发生!"
            print(error_msg)
            raise ConnectionError(error_msg)

    def decorator(self, func):
        """装饰器：给函数注入故障"""
        @wraps(func)#确保 wrapper 函数继承了原始函数 func 的元数据
        async def wrapper(*args, **kwargs):
            self.simulate(func.__name__)
            return await func(*args, **kwargs)
        return wrapper

chaos = ChaosMonkey()