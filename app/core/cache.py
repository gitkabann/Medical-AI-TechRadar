import json
import hashlib
from functools import wraps
from app.core.event_bus import bus  # 复用 redis 连接
from app.core.logger import get_logger

logger = get_logger("Cache")

def cache_result(ttl_seconds=3600, key_prefix="cache"):
    """
    装饰器：缓存函数返回结果到 Redis
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. 生成 Cache Key
            # 将 args 和 kwargs 序列化后做 hash
            arg_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str) # 参数转为字符串
            key_hash = hashlib.md5(arg_str.encode()).hexdigest() # 对序列化后的参数字符串进行 MD5 哈希计算，生成一个固定长度的摘要
            cache_key = f"{key_prefix}:{func.__name__}:{key_hash}"#将用户定义的 key_prefix、函数名 func.__name__ 和参数哈希值 key_hash 组合，形成Redis Key

            # 2. 尝试读取缓存
            cached_val = bus.redis.get(cache_key)
            if cached_val: # 如果缓存存在，直接返回反序列化结果
                logger.info(f"⚡ [Cache] Hit: {func.__name__}")
                return json.loads(cached_val)

            # 3. 执行原函数
            result = func(*args, **kwargs)

            # 4. 写入缓存
            try:
                bus.redis.set(cache_key, json.dumps(result, default=str), ex=ttl_seconds)
            except Exception as e:
                logger.warning(f"缓存写入失败: {e}")

            return result
        return wrapper
    return decorator