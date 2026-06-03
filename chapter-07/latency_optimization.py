# latency_optimization.py
"""Optimize RAG system for low latency."""

from functools import lru_cache
from typing import List, Optional
import hashlib
import json


class CachedRAG:
    """RAG system with query caching."""

    def __init__(self, query_engine, cache_size: int = 100) -> None:
        self.query_engine = query_engine
        self.cache_size = cache_size
        self._cache: dict = {}

    def _hash_query(self, query: str) -> str:
        """Create a hash of the query for caching."""
        return hashlib.md5(query.encode()).hexdigest()

    def query(self, query: str) -> str:
        """Query with caching."""
        query_hash = self._hash_query(query)

        if query_hash in self._cache:
            return self._cache[query_hash]

        result = self.query_engine.query(query)

        # Cache the result
        if len(self._cache) >= self.cache_size:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))

        self._cache[query_hash] = str(result)

        return str(result)
