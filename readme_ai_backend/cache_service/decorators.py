from functools import wraps
from typing import Any, Callable
from .cache import CacheService

cache_service = CacheService()

def cached(ttl_seconds: int = 300):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create a unique cache key based on function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = cache_service.get(cache_key)
            if result is not None:
                return result
                
            # If not in cache, execute function and store result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl_seconds)
            return result
            
        return wrapper
    return decorator
