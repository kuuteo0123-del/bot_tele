"""ุ
⏱️ RATE LIMITER - Chống auto-ban
"""

import time
from logger_setup import logger
from config import Config
from collections import deque

class RateLimiter:
    """Rate limiter - anti-ban"""
    
    def __init__(self, requests_per_minute: int = 30, max_burst: int = 5):
        self.requests_per_minute = requests_per_minute
        self.max_burst = max_burst
        self.requests = deque()  # (timestamp, username)
    
    def is_allowed(self, username: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Remove old requests (older than 1 minute)
        while self.requests and self.requests[0][0] < now - 60:
            self.requests.popleft()
        
        # Count requests from this user
        user_requests = sum(1 for t, u in self.requests if u == username)
        if user_requests >= self.max_burst:
            return False
        
        # Check total requests
        if len(self.requests) >= self.requests_per_minute:
            return False
        
        return True
    
    def add_request(self, username: str):
        """Add request"""
        self.requests.append((time.time(), username))

# Global instance
_rate_limiter = None

def init_anti_detection() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(
            Config.REQUESTS_PER_MINUTE,
            Config.MAX_BURST
        )
    return _rate_limiter

def get_anti_detection() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        init_anti_detection()
    return _rate_limiter
