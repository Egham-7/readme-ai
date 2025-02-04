from typing import Any, Optional
from datetime import datetime, timedelta
import json

class CacheService:
    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def set(self, repo_url: str, content: dict, ttl_seconds: int = 3600) -> None:
        cache_key = self._generate_cache_key(repo_url)
        self._cache[cache_key] = content
        self._expiry[cache_key] = datetime.now() + timedelta(seconds=ttl_seconds)

    def get(self, repo_url: str) -> Optional[dict]:
        cache_key = self._generate_cache_key(repo_url)
        if cache_key not in self._cache:
            return None
            
        if datetime.now() > self._expiry[cache_key]:
            self.delete(cache_key)
            return None
            
        return self._cache[cache_key]

    def delete(self, cache_key: str) -> None:
        self._cache.pop(cache_key, None)
        self._expiry.pop(cache_key, None)

    def _generate_cache_key(self, repo_url: str) -> str:
        return f"readme_gen:{repo_url}"