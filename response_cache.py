"""
Simple Response Caching Module
Модуль кэширования ответов

This module provides basic caching for frequently asked questions
to improve response times and reduce API calls.
"""

import hashlib
import json
import logging
import time
from typing import Dict, Optional, Any
from collections import OrderedDict

logger = logging.getLogger(__name__)


class ResponseCache:
    """Simple in-memory cache for AI responses with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of cached responses
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.hits = 0
        self.misses = 0
        
    def _generate_cache_key(self, user_message: str, agent_type: str, language: str) -> str:
        """Generate cache key from message parameters"""
        # Normalize message for better cache hits
        normalized_message = user_message.lower().strip()
        
        # Create unique key
        key_data = {
            'message': normalized_message,
            'agent': agent_type,
            'language': language
        }
        
        # Use SHA256 hash for consistent key generation
        key_string = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()[:16]
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        if 'expires_at' not in cache_entry:
            return True
            
        return time.time() > cache_entry['expires_at']
    
    def _cleanup_expired(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items() 
            if current_time > entry.get('expires_at', 0)
        ]
        
        for key in expired_keys:
            del self.cache[key]
            
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _evict_oldest(self):
        """Remove oldest entries to maintain max_size"""
        while len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Evicted oldest cache entry: {oldest_key}")
    
    def get(self, user_message: str, agent_type: str, language: str = 'ru') -> Optional[Dict[str, Any]]:
        """
        Get cached response if available and not expired
        
        Returns:
            Cached response dict or None if not found/expired
        """
        try:
            cache_key = self._generate_cache_key(user_message, agent_type, language)
            
            # Clean up expired entries periodically
            if len(self.cache) > 0 and (self.hits + self.misses) % 10 == 0:
                self._cleanup_expired()
            
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                
                if not self._is_expired(entry):
                    # Move to end (LRU behavior)
                    self.cache.move_to_end(cache_key)
                    self.hits += 1
                    
                    logger.debug(f"Cache hit for message: '{user_message[:50]}...'")
                    return entry['response']
                else:
                    # Remove expired entry
                    del self.cache[cache_key]
            
            self.misses += 1
            return None
            
        except Exception as e:
            logger.error(f"Error accessing cache: {e}")
            return None
    
    def set(self, user_message: str, agent_type: str, response_data: Dict[str, Any], 
            language: str = 'ru', ttl: Optional[int] = None) -> bool:
        """
        Cache a response
        
        Args:
            user_message: Original user message
            agent_type: Type of agent that handled the request
            response_data: Response data to cache
            language: Language of the interaction
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if cached successfully
        """
        try:
            cache_key = self._generate_cache_key(user_message, agent_type, language)
            
            # Calculate expiration time
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            
            # Evict old entries if needed
            self._evict_oldest()
            
            # Store in cache
            cache_entry = {
                'response': response_data,
                'cached_at': time.time(),
                'expires_at': expires_at,
                'agent_type': agent_type,
                'language': language
            }
            
            self.cache[cache_key] = cache_entry
            
            logger.debug(f"Cached response for message: '{user_message[:50]}...' "
                        f"(TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False
    
    def clear(self):
        """Clear all cached responses"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'cache_size': len(self.cache),
            'max_size': self.max_size
        }
    
    def should_cache(self, user_message: str, response_data: Dict[str, Any]) -> bool:
        """
        Determine if a response should be cached based on heuristics
        
        Args:
            user_message: User's question
            response_data: Generated response data
            
        Returns:
            True if response should be cached
        """
        # Don't cache very short messages (likely greetings)
        if len(user_message.strip()) < 10:
            return False
        
        # Don't cache if response has low confidence
        confidence = response_data.get('confidence', 0)
        if confidence < 0.5:
            return False
        
        # Don't cache error responses
        if 'error' in response_data.get('response', '').lower():
            return False
        
        # Don't cache very short responses (likely errors)
        response_text = response_data.get('response', '')
        if len(response_text) < 50:
            return False
        
        return True


# Global cache instance
response_cache = ResponseCache(max_size=500, default_ttl=1800)  # 30 minutes TTL