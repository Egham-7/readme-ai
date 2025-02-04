from typing import Any, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self._cache = {}
        self._expiry = {}
        self.DEFAULT_TTL = 24 * 60 * 60  # 24 hours in seconds

    def set(self, repo_url: str, content: str, ttl_seconds: int = None) -> None:
        """Set cache entry with TTL"""
        cache_key = self._generate_cache_key(repo_url)
        self._cache[cache_key] = content
        ttl = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL
        self._expiry[cache_key] = datetime.now() + timedelta(seconds=ttl)
        logger.info(f"Cached {repo_url} with {ttl/3600:.1f} hour TTL")

    def get(self, repo_url: str) -> Optional[str]:
        """Get cache entry if exists and not expired"""
        cache_key = self._generate_cache_key(repo_url)
        
        if cache_key not in self._cache:
            return None

        if datetime.now() > self._expiry[cache_key]:
            logger.info(f"Cache expired for {repo_url}")
            self.delete(cache_key)
            return None

        remaining_ttl = (self._expiry[cache_key] - datetime.now()).total_seconds()
        logger.info(f"Cache hit for {repo_url} - {remaining_ttl/3600:.1f} hours remaining")
        return self._cache[cache_key]
    

    def delete(self, cache_key: str) -> None:
        """Remove cache entry"""
        self._cache.pop(cache_key, None)
        self._expiry.pop(cache_key, None)
        logger.info(f"Removed cache entry: {cache_key}")

    def _generate_cache_key(self, repo_url: str) -> str:
        """Generate consistent cache key for repo URL"""
        return f"readme_gen:{repo_url}"
