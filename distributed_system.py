"""
Distributed Caching and Async Processing System
Система распределенного кэширования и асинхронной обработки

This module provides enhanced caching with Redis support and
asynchronous processing capabilities for better scalability.
"""

import logging
import asyncio
import json
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty
import hashlib

logger = logging.getLogger(__name__)


class DistributedCache:
    """Distributed caching system with Redis fallback to in-memory"""
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        self.redis_client = None
        self.redis_available = False
        self.default_ttl = default_ttl
        
        # Fallback to in-memory cache
        from response_cache import ResponseCache
        self.memory_cache = ResponseCache(max_size=1000, default_ttl=default_ttl)
        
        # Try to initialize Redis if URL provided
        if redis_url:
            self._init_redis(redis_url)
        
        # Cache statistics
        self.stats = {
            'redis_hits': 0,
            'redis_misses': 0,
            'memory_hits': 0,
            'memory_misses': 0,
            'redis_errors': 0
        }
    
    def _init_redis(self, redis_url: str):
        """Initialize Redis connection"""
        try:
            import redis
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info("Redis distributed cache initialized successfully")
            
        except ImportError:
            logger.warning("Redis library not available, using memory cache only")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}, using memory cache only")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from distributed cache"""
        try:
            # Try Redis first if available
            if self.redis_available and self.redis_client:
                try:
                    value = self.redis_client.get(key)
                    if value is not None:
                        self.stats['redis_hits'] += 1
                        return json.loads(value)
                    else:
                        self.stats['redis_misses'] += 1
                except Exception as e:
                    logger.error(f"Redis get error: {e}")
                    self.stats['redis_errors'] += 1
            
            # Fallback to memory cache - create a simple key for compatibility
            simple_key = key.replace(':', '_')
            result = self.memory_cache.get(simple_key, 'unknown', 'ru')
            
            if result:
                self.stats['memory_hits'] += 1
                return result
            else:
                self.stats['memory_misses'] += 1
                return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in distributed cache"""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, ensure_ascii=False)
            
            # Try Redis first if available
            if self.redis_available and self.redis_client:
                try:
                    self.redis_client.setex(key, ttl, serialized_value)
                    logger.debug(f"Cached in Redis: {key}")
                except Exception as e:
                    logger.error(f"Redis set error: {e}")
                    self.stats['redis_errors'] += 1
            
            # Always cache in memory as fallback
            # Create a simple key for memory cache compatibility
            simple_key = key.replace(':', '_')
            self.memory_cache.set(simple_key, 'unknown', value, 'ru', ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from distributed cache"""
        try:
            deleted = False
            
            # Delete from Redis if available
            if self.redis_available and self.redis_client:
                try:
                    result = self.redis_client.delete(key)
                    deleted = result > 0
                except Exception as e:
                    logger.error(f"Redis delete error: {e}")
                    self.stats['redis_errors'] += 1
            
            # Note: Memory cache doesn't have direct delete by key
            # This is a limitation of the fallback approach
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            # Clear Redis if available
            if self.redis_available and self.redis_client:
                try:
                    self.redis_client.flushdb()
                except Exception as e:
                    logger.error(f"Redis clear error: {e}")
                    self.stats['redis_errors'] += 1
            
            # Clear memory cache
            self.memory_cache.clear()
            
            logger.info("Distributed cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        memory_stats = self.memory_cache.get_stats()
        
        total_hits = self.stats['redis_hits'] + self.stats['memory_hits']
        total_misses = self.stats['redis_misses'] + self.stats['memory_misses']
        total_requests = total_hits + total_misses
        
        return {
            'redis_available': self.redis_available,
            'redis_stats': {
                'hits': self.stats['redis_hits'],
                'misses': self.stats['redis_misses'],
                'errors': self.stats['redis_errors']
            },
            'memory_stats': memory_stats,
            'combined_stats': {
                'total_hits': total_hits,
                'total_misses': total_misses,
                'hit_rate': round(total_hits / total_requests * 100, 2) if total_requests > 0 else 0,
                'total_requests': total_requests
            }
        }


class AsyncTaskProcessor:
    """Asynchronous task processing system for heavy operations"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = Queue()
        self.results = {}
        self.task_counter = 0
        self.processing = True
        
        # Start background processor
        self.processor_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.processor_thread.start()
        
        # Task statistics
        self.stats = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'average_processing_time': 0.0
        }
        
        logger.info(f"Async task processor initialized with {max_workers} workers")
    
    def submit_task(self, task_func: Callable, *args, **kwargs) -> str:
        """Submit task for asynchronous processing"""
        task_id = f"task_{self.task_counter}_{int(time.time())}"
        self.task_counter += 1
        
        task = {
            'id': task_id,
            'function': task_func,
            'args': args,
            'kwargs': kwargs,
            'submitted_at': time.time()
        }
        
        self.task_queue.put(task)
        self.stats['tasks_submitted'] += 1
        
        logger.debug(f"Submitted async task: {task_id}")
        return task_id
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[Any]:
        """Get result of async task"""
        start_time = time.time()
        
        while True:
            if task_id in self.results:
                result = self.results.pop(task_id)
                if result['status'] == 'completed':
                    return result['data']
                elif result['status'] == 'failed':
                    raise Exception(f"Task failed: {result['error']}")
            
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            time.sleep(0.1)  # Small delay to avoid busy waiting
    
    def _process_tasks(self):
        """Background task processor"""
        while self.processing:
            try:
                task = self.task_queue.get(timeout=1.0)
                self._execute_task(task)
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Task processor error: {e}")
    
    def _execute_task(self, task: Dict[str, Any]):
        """Execute a single task"""
        task_id = task['id']
        start_time = time.time()
        
        try:
            # Execute task function
            result = task['function'](*task['args'], **task['kwargs'])
            
            # Store result
            processing_time = time.time() - start_time
            self.results[task_id] = {
                'status': 'completed',
                'data': result,
                'processing_time': processing_time
            }
            
            # Update statistics
            self.stats['tasks_completed'] += 1
            self._update_average_processing_time(processing_time)
            
            logger.debug(f"Task completed: {task_id} in {processing_time:.2f}s")
            
        except Exception as e:
            # Store error
            self.results[task_id] = {
                'status': 'failed',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
            
            self.stats['tasks_failed'] += 1
            logger.error(f"Task failed: {task_id} - {e}")
    
    def _update_average_processing_time(self, new_time: float):
        """Update average processing time"""
        total_completed = self.stats['tasks_completed']
        if total_completed == 1:
            self.stats['average_processing_time'] = new_time
        else:
            current_avg = self.stats['average_processing_time']
            # Weighted average with more weight on recent tasks
            self.stats['average_processing_time'] = (current_avg * 0.9 + new_time * 0.1)
    
    def get_task_status(self, task_id: str) -> str:
        """Get status of a task"""
        if task_id in self.results:
            return self.results[task_id]['status']
        else:
            return 'pending'
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        return {
            'max_workers': self.max_workers,
            'queue_size': self.task_queue.qsize(),
            'pending_results': len(self.results),
            'statistics': self.stats.copy()
        }
    
    def shutdown(self):
        """Shutdown the processor"""
        self.processing = False
        self.executor.shutdown(wait=True)
        logger.info("Async task processor shutdown")


class PerformanceOptimizer:
    """Performance optimization coordinator"""
    
    def __init__(self, distributed_cache: DistributedCache, 
                 async_processor: AsyncTaskProcessor):
        self.cache = distributed_cache
        self.async_processor = async_processor
        
        # Performance thresholds
        self.thresholds = {
            'slow_response_time': 3.0,  # seconds
            'low_cache_hit_rate': 0.25,  # 25%
            'high_queue_size': 10,      # tasks
            'error_rate_limit': 0.05     # 5%
        }
        
        # Optimization strategies
        self.optimizations = {
            'precompute_popular_queries': True,
            'aggressive_caching': False,
            'async_knowledge_search': True,
            'response_compression': True
        }
    
    def optimize_response_generation(self, user_message: str, agent_type: str, 
                                   language: str = 'ru') -> Dict[str, Any]:
        """Optimize response generation with caching and async processing"""
        optimization_start = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(user_message, agent_type, language)
        
        # Check distributed cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for optimized response: {cache_key}")
            return {
                'response': cached_result,
                'cached': True,
                'optimization_time': time.time() - optimization_start,
                'source': 'distributed_cache'
            }
        
        # If enabled, submit to async processing for complex queries
        if (self.optimizations['async_knowledge_search'] and 
            len(user_message) > 50):  # Complex query heuristic
            
            logger.debug(f"Submitting complex query to async processing: {user_message[:50]}...")
            return {
                'async_processing': True,
                'optimization_time': time.time() - optimization_start,
                'message': 'Processing your request asynchronously...'
            }
        
        return {
            'optimization_applied': False,
            'optimization_time': time.time() - optimization_start
        }
    
    def precompute_popular_queries(self, popular_queries: List[Dict[str, str]]):
        """Precompute responses for popular queries"""
        if not self.optimizations['precompute_popular_queries']:
            return
        
        logger.info(f"Precomputing {len(popular_queries)} popular queries...")
        
        for query_data in popular_queries:
            message = query_data.get('message', '')
            agent_type = query_data.get('agent_type', '')
            language = query_data.get('language', 'ru')
            
            # Submit for async processing
            task_id = self.async_processor.submit_task(
                self._compute_response,
                message, agent_type, language
            )
            
            logger.debug(f"Submitted precomputation task: {task_id}")
    
    def _compute_response(self, message: str, agent_type: str, language: str) -> Dict[str, Any]:
        """Compute response (placeholder for actual response generation)"""
        # This would integrate with the actual agent system
        # For now, return a placeholder
        time.sleep(0.5)  # Simulate processing time
        
        return {
            'message': message,
            'agent_type': agent_type,
            'language': language,
            'computed_at': time.time(),
            'precomputed': True
        }
    
    def _generate_cache_key(self, message: str, agent_type: str, language: str) -> str:
        """Generate optimized cache key"""
        # Normalize message for better cache hits
        normalized_message = message.lower().strip()
        
        # Create hash for key
        key_data = f"{normalized_message}:{agent_type}:{language}"
        key_hash = hashlib.md5(key_data.encode('utf-8')).hexdigest()[:12]
        
        return f"optimized:{key_hash}:{agent_type}:{language}"
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze system performance and suggest optimizations"""
        cache_stats = self.cache.get_stats()
        processor_stats = self.async_processor.get_stats()
        
        analysis = {
            'cache_performance': self._analyze_cache_performance(cache_stats),
            'processing_performance': self._analyze_processing_performance(processor_stats),
            'recommendations': []
        }
        
        # Generate recommendations
        cache_hit_rate = cache_stats['combined_stats']['hit_rate'] / 100
        if cache_hit_rate < self.thresholds['low_cache_hit_rate']:
            analysis['recommendations'].append(
                f"Low cache hit rate ({cache_hit_rate:.1%}). Consider enabling aggressive caching."
            )
        
        avg_processing_time = processor_stats['statistics']['average_processing_time']
        if avg_processing_time > self.thresholds['slow_response_time']:
            analysis['recommendations'].append(
                f"Slow average processing time ({avg_processing_time:.2f}s). Consider optimizing algorithms."
            )
        
        queue_size = processor_stats['queue_size']
        if queue_size > self.thresholds['high_queue_size']:
            analysis['recommendations'].append(
                f"High queue size ({queue_size}). Consider adding more workers."
            )
        
        return analysis
    
    def _analyze_cache_performance(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cache performance"""
        combined = stats['combined_stats']
        
        return {
            'hit_rate': combined['hit_rate'],
            'total_requests': combined['total_requests'],
            'redis_available': stats['redis_available'],
            'performance_rating': self._calculate_cache_rating(combined['hit_rate'])
        }
    
    def _analyze_processing_performance(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze processing performance"""
        statistics = stats['statistics']
        
        total_tasks = statistics['tasks_completed'] + statistics['tasks_failed']
        error_rate = statistics['tasks_failed'] / total_tasks if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'error_rate': error_rate,
            'average_time': statistics['average_processing_time'],
            'queue_size': stats['queue_size'],
            'performance_rating': self._calculate_processing_rating(
                statistics['average_processing_time'], error_rate
            )
        }
    
    def _calculate_cache_rating(self, hit_rate: float) -> str:
        """Calculate cache performance rating"""
        if hit_rate >= 70:
            return "Excellent"
        elif hit_rate >= 50:
            return "Good"
        elif hit_rate >= 30:
            return "Fair"
        else:
            return "Poor"
    
    def _calculate_processing_rating(self, avg_time: float, error_rate: float) -> str:
        """Calculate processing performance rating"""
        if avg_time <= 1.0 and error_rate <= 0.01:
            return "Excellent"
        elif avg_time <= 2.0 and error_rate <= 0.03:
            return "Good"
        elif avg_time <= 3.0 and error_rate <= 0.05:
            return "Fair"
        else:
            return "Poor"
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {
            'thresholds': self.thresholds,
            'optimizations_enabled': self.optimizations,
            'cache_stats': self.cache.get_stats(),
            'processor_stats': self.async_processor.get_stats()
        }


# Global instances
distributed_cache = DistributedCache()
async_processor = AsyncTaskProcessor(max_workers=4)
performance_optimizer = PerformanceOptimizer(distributed_cache, async_processor)