"""Response caching layer with TTL-based invalidation for Regen MCP server.

This module provides intelligent caching for expensive blockchain queries with
configurable TTL, memory optimization, and cache performance metrics.
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata and TTL tracking."""
    data: Any
    timestamp: float
    ttl_seconds: int
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl_seconds
    
    def is_valid(self) -> bool:
        """Check if cache entry is still valid."""
        return not self.is_expired()
    
    def access(self):
        """Mark cache entry as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / max(1, total)) * 100
    
    @property
    def size_mb(self) -> float:
        """Get cache size in megabytes."""
        return self.size_bytes / (1024 * 1024)


class RegenCacheManager:
    """Advanced caching system for Regen Network blockchain queries.
    
    Features:
    - TTL-based expiration with configurable periods
    - Memory usage optimization with LRU eviction
    - Per-query-type cache configuration
    - Performance metrics and monitoring
    - Async-safe operations
    - Intelligent cache warming
    """
    
    def __init__(
        self,
        max_size_mb: int = 100,
        default_ttl_seconds: int = 300,  # 5 minutes
        cleanup_interval_seconds: int = 60,  # 1 minute
        enable_metrics: bool = True
    ):
        """Initialize cache manager.
        
        Args:
            max_size_mb: Maximum cache size in megabytes
            default_ttl_seconds: Default TTL for cache entries
            cleanup_interval_seconds: Interval between cleanup operations
            enable_metrics: Whether to collect performance metrics
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl_seconds
        self.cleanup_interval = cleanup_interval_seconds
        self.enable_metrics = enable_metrics
        
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._metrics = CacheMetrics()
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Query-specific TTL configuration
        self._ttl_config = {
            # Fast-changing data (short TTL)
            "sell_orders": 60,      # 1 minute
            "market_statistics": 120,  # 2 minutes
            "portfolio_analysis": 180,  # 3 minutes
            
            # Moderate-changing data (medium TTL) 
            "basket_balances": 300,  # 5 minutes
            "account_balances": 300,  # 5 minutes
            "chain_status": 300,     # 5 minutes
            
            # Slow-changing data (long TTL)
            "credit_classes": 3600,   # 1 hour
            "credit_types": 3600,     # 1 hour
            "projects": 1800,         # 30 minutes
            "chain_config": 7200,     # 2 hours
            
            # Very slow-changing data (very long TTL)
            "credit_batches": 1800,   # 30 minutes (batches can change when retired)
            "baskets": 1800,          # 30 minutes
        }
    
    def start_cleanup_task(self):
        """Start the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Started cache cleanup task")
    
    async def stop_cleanup_task(self):
        """Stop the background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped cache cleanup task")
    
    async def _cleanup_loop(self):
        """Background task for periodic cache cleanup."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_expired()
                await self.enforce_size_limit()
            except asyncio.CancelledError:
                logger.info("Cache cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    def _generate_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate a cache key from function name and parameters."""
        # Create deterministic string from arguments
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else []
        }
        
        # Hash for consistent key generation
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _estimate_size(self, data: Any) -> int:
        """Estimate memory size of cached data."""
        try:
            # Simple estimate based on JSON serialization
            json_str = json.dumps(data, default=str)
            return len(json_str.encode('utf-8'))
        except Exception:
            # Fallback estimate
            return 1024  # 1KB default
    
    def _get_ttl_for_query(self, func_name: str) -> int:
        """Get appropriate TTL for a specific query type."""
        # Look for matching patterns in function name
        for pattern, ttl in self._ttl_config.items():
            if pattern in func_name.lower():
                return ttl
        
        return self.default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached data by key."""
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                if self.enable_metrics:
                    self._metrics.misses += 1
                return None
            
            if entry.is_expired():
                # Remove expired entry
                del self._cache[key]
                if self.enable_metrics:
                    self._metrics.misses += 1
                    self._metrics.entry_count -= 1
                    self._metrics.size_bytes -= entry.size_bytes
                return None
            
            # Update access tracking
            entry.access()
            if self.enable_metrics:
                self._metrics.hits += 1
            
            return entry.data
    
    async def set(self, key: str, data: Any, ttl_seconds: Optional[int] = None, func_name: str = "") -> bool:
        """Set cached data with TTL."""
        if ttl_seconds is None:
            ttl_seconds = self._get_ttl_for_query(func_name)
        
        size_bytes = self._estimate_size(data)
        
        async with self._lock:
            # Check if adding this entry would exceed size limit
            current_size = self._metrics.size_bytes if self.enable_metrics else sum(e.size_bytes for e in self._cache.values())
            
            if current_size + size_bytes > self.max_size_bytes:
                # Try to make space by removing expired entries first
                await self._cleanup_expired_unsafe()
                
                # If still over limit, perform LRU eviction
                if current_size + size_bytes > self.max_size_bytes:
                    await self._evict_lru_unsafe(size_bytes)
            
            entry = CacheEntry(
                data=data,
                timestamp=time.time(),
                ttl_seconds=ttl_seconds,
                size_bytes=size_bytes
            )
            
            # Remove old entry if exists
            old_entry = self._cache.get(key)
            if old_entry and self.enable_metrics:
                self._metrics.size_bytes -= old_entry.size_bytes
                self._metrics.entry_count -= 1
            
            self._cache[key] = entry
            
            if self.enable_metrics:
                self._metrics.size_bytes += size_bytes
                if old_entry is None:
                    self._metrics.entry_count += 1
            
            return True
    
    async def _cleanup_expired_unsafe(self):
        """Remove expired entries (unsafe - assumes lock is held)."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time - entry.timestamp > entry.ttl_seconds
        ]
        
        for key in expired_keys:
            entry = self._cache.pop(key)
            if self.enable_metrics:
                self._metrics.size_bytes -= entry.size_bytes
                self._metrics.entry_count -= 1
    
    async def _evict_lru_unsafe(self, needed_bytes: int):
        """Evict least recently used entries (unsafe - assumes lock is held)."""
        if not self._cache:
            return
        
        # Sort by last access time (oldest first)
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        bytes_freed = 0
        evicted_count = 0
        
        for key, entry in sorted_entries:
            if bytes_freed >= needed_bytes:
                break
            
            del self._cache[key]
            bytes_freed += entry.size_bytes
            evicted_count += 1
            
            if self.enable_metrics:
                self._metrics.size_bytes -= entry.size_bytes
                self._metrics.entry_count -= 1
                self._metrics.evictions += 1
        
        logger.info(f"Evicted {evicted_count} entries, freed {bytes_freed} bytes")
    
    async def cleanup_expired(self):
        """Remove all expired cache entries."""
        async with self._lock:
            await self._cleanup_expired_unsafe()
    
    async def enforce_size_limit(self):
        """Enforce maximum cache size limit."""
        async with self._lock:
            if self._metrics.size_bytes > self.max_size_bytes:
                excess_bytes = self._metrics.size_bytes - self.max_size_bytes
                await self._evict_lru_unsafe(excess_bytes)
    
    async def clear(self):
        """Clear all cached data."""
        async with self._lock:
            self._cache.clear()
            self._metrics = CacheMetrics()
    
    async def get_metrics(self) -> CacheMetrics:
        """Get current cache performance metrics."""
        if not self.enable_metrics:
            return CacheMetrics()
        
        async with self._lock:
            # Update current size metrics
            current_size = sum(entry.size_bytes for entry in self._cache.values())
            self._metrics.size_bytes = current_size
            self._metrics.entry_count = len(self._cache)
            
            return CacheMetrics(
                hits=self._metrics.hits,
                misses=self._metrics.misses,
                evictions=self._metrics.evictions,
                size_bytes=self._metrics.size_bytes,
                entry_count=self._metrics.entry_count
            )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get detailed cache statistics."""
        metrics = await self.get_metrics()
        
        # Calculate age distribution
        current_time = time.time()
        age_buckets = {"<1min": 0, "1-5min": 0, "5-30min": 0, ">30min": 0}
        
        async with self._lock:
            for entry in self._cache.values():
                age_seconds = current_time - entry.timestamp
                
                if age_seconds < 60:
                    age_buckets["<1min"] += 1
                elif age_seconds < 300:
                    age_buckets["1-5min"] += 1
                elif age_seconds < 1800:
                    age_buckets["5-30min"] += 1
                else:
                    age_buckets[">30min"] += 1
        
        return {
            "performance": {
                "hit_rate_percent": round(metrics.hit_rate, 2),
                "total_hits": metrics.hits,
                "total_misses": metrics.misses,
                "total_evictions": metrics.evictions
            },
            "storage": {
                "size_mb": round(metrics.size_mb, 2),
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "utilization_percent": round((metrics.size_bytes / self.max_size_bytes) * 100, 2),
                "entry_count": metrics.entry_count
            },
            "age_distribution": age_buckets,
            "configuration": {
                "default_ttl_seconds": self.default_ttl,
                "cleanup_interval_seconds": self.cleanup_interval,
                "metrics_enabled": self.enable_metrics
            },
            "ttl_configuration": self._ttl_config,
            "generated_at": datetime.utcnow().isoformat()
        }


# Global cache manager instance
_cache_manager: Optional[RegenCacheManager] = None


def get_cache_manager() -> RegenCacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = RegenCacheManager()
        # Note: cleanup task should be started when server starts
    return _cache_manager


def cached(ttl_seconds: Optional[int] = None):
    """Decorator for caching async function results.
    
    Args:
        ttl_seconds: TTL for cached result. If None, uses query-type specific TTL.
    
    Usage:
        @cached(ttl_seconds=300)
        async def expensive_query():
            # ... expensive operation
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            cache_key = cache._generate_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache first
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}, executing...")
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache.set(cache_key, result, ttl_seconds, func.__name__)
            
            return result
        
        return wrapper
    return decorator


# Convenience decorators for common cache TTLs
def cached_short(func: Callable):
    """Cache with short TTL (1 minute) for rapidly changing data."""
    return cached(ttl_seconds=60)(func)


def cached_medium(func: Callable):
    """Cache with medium TTL (5 minutes) for moderately changing data.""" 
    return cached(ttl_seconds=300)(func)


def cached_long(func: Callable):
    """Cache with long TTL (1 hour) for slowly changing data."""
    return cached(ttl_seconds=3600)(func)


async def warm_cache(client_method: Callable, *args, **kwargs):
    """Warm cache by pre-loading commonly accessed data.
    
    Args:
        client_method: Client method to call
        *args, **kwargs: Arguments to pass to method
    """
    try:
        logger.info(f"Warming cache for {client_method.__name__}")
        await client_method(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Cache warming failed for {client_method.__name__}: {e}")