"""ุ
🛡️ ERROR HANDLER - Xử lý lỗi & retry
"""

import asyncio
from logger_setup import logger

class RetryHandler:
    """Retry handler"""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        self.max_retries = max_retries
        self.delay = delay
    
    async def retry(self, func, *args, **kwargs):
        """Retry function"""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"⚠️ Retry {attempt + 1}/{self.max_retries}: {e}")
                    await asyncio.sleep(self.delay)
                else:
                    logger.error(f"❌ All retries failed: {e}")
                    raise

class CircuitBreaker:
    """Circuit breaker pattern"""
    
    def __init__(self, failure_threshold: int = 5):
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.is_open = False
    
    async def call(self, func, *args, **kwargs):
        """Call function with circuit breaker"""
        if self.is_open:
            raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                logger.error("🔴 Circuit breaker OPEN")
            raise

# Global instances
_retry_handler = None
_circuit_breaker = None

def get_retry_handler() -> RetryHandler:
    global _retry_handler
    if _retry_handler is None:
        _retry_handler = RetryHandler()
    return _retry_handler

def get_circuit_breaker() -> CircuitBreaker:
    global _circuit_breaker
    if _circuit_breaker is None:
        _circuit_breaker = CircuitBreaker()
    return _circuit_breaker
