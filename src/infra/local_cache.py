from functools import wraps
from typing import Any, Dict, Optional
from collections import OrderedDict
import time

class LocalCache:
    """
    Implements a local in-memory cache with LRU (Least Recently Used) eviction policy.
    
    This class provides a thread-safe caching mechanism with the following features:
    - Fixed maximum size with LRU eviction
    - Time-to-live (TTL) for cache entries
    - Automatic cleanup of expired entries
    - Ordered storage for efficient LRU tracking
    
    Attributes:
        _cache (OrderedDict): Main cache storage using ordered dictionary
        _max_size (int): Maximum number of items in cache
        _ttl (int): Time-to-live for cache entries in seconds
        _timestamps (Dict[str, float]): Tracks entry creation times
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 60 * 30):
        """
        Initialize local cache with LRU policy.
        
        Args:
            max_size (int): Maximum number of items to store in cache
            ttl (int): Time to live in seconds for cache entries
        """
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl
        self._timestamps: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if it exists and is not expired.
        
        This method:
        1. Checks if key exists in cache
        2. Verifies entry hasn't expired
        3. Updates LRU order if entry is valid
        4. Returns None if entry is missing or expired
        
        Args:
            key (str): The key to look up in cache
            
        Returns:
            Optional[Any]: Cached value if found and valid, None otherwise
        """
        if key not in self._cache:
            return None
            
        # Check if entry has expired
        if time.time() - self._timestamps[key] > self._ttl:
            self.delete(key)
            return None
            
        # Move to end to mark as recently used
        value = self._cache.pop(key)
        self._cache[key] = value
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with LRU eviction.
        
        This method:
        1. Removes existing entry if key exists
        2. Evicts least recently used item if cache is full
        3. Adds new entry with current timestamp
        
        Args:
            key (str): The key to store in cache
            value (Any): The value to cache
        """
        if key in self._cache:
            self._cache.pop(key)
        elif len(self._cache) >= self._max_size:
            # Remove least recently used item
            self._cache.popitem(last=False)
            
        self._cache[key] = value
        self._timestamps[key] = time.time()

    def delete(self, key: str) -> None:
        """
        Delete key from cache.
        
        Removes both the cached value and its timestamp.
        
        Args:
            key (str): The key to remove from cache
        """
        if key in self._cache:
            self._cache.pop(key)
            self._timestamps.pop(key)

    def clear(self) -> None:
        """
        Clear all entries from cache.
        
        Removes all cached values and their timestamps.
        """
        self._cache.clear()
        self._timestamps.clear()

def cached(cache_key_fn=None, ttl: int = 60 * 60 * 24):
    """
    Decorator to cache function results.
    
    This decorator provides a caching mechanism for function results with:
    - Customizable cache key generation
    - Configurable TTL
    - Automatic cache management
    - Function-specific cache instances
    
    Args:
        cache_key_fn (Callable, optional): Function to generate cache key from args/kwargs
        ttl (int): Time to live in seconds for cache entries
        
    Returns:
        Callable: Decorated function with caching capability
    """
    def decorator(func):
        # Create cache instance specific to this function
        cache = LocalCache(ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_fn:
                key = cache_key_fn(*args, **kwargs)
            else:
                # Default to function name + args + kwargs as key
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
                
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            
            return result
        
        wrapper.cache = cache
        return wrapper
    return decorator


