"""
⏱️ RATE LIMITER & ANTI-BAN SYSTEM (v3.6 - OPTIMIZED)
Kiểm soát tốc độ gửi để tránh bị ban - OPTIMIZED FOR SPEED
"""

import time
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Optional
from logger_setup import logger


class RateLimiter:
    """Rate limiter cho account - OPTIMIZED"""
    
    def __init__(self, 
                 min_delay: float = 0.8,
                 requests_per_minute: int = 30):
        """
        min_delay: Minimum delay giữa 2 requests (giây)
        requests_per_minute: Max requests per minute (30 = 2s average)
        """
        self.min_delay = min_delay
        self.requests_per_minute = requests_per_minute
        self.last_request = {}
        self.request_history = {}
        self.logger_prefix = "⏱️ RATE LIMITER"
    
    async def wait_if_needed(self, account: str) -> float:
        """Chờ nếu cần để maintain rate limit"""
        current_time = time.time()
        
        if account in self.last_request:
            elapsed = current_time - self.last_request[account]
            if elapsed < self.min_delay:
                wait_time = self.min_delay - elapsed
                logger.debug(f"{self.logger_prefix} [{account}] ⏳ {wait_time:.3f}s...")
                await asyncio.sleep(wait_time)
                current_time = time.time()
        
        if account not in self.request_history:
            self.request_history[account] = []
        
        cutoff_time = current_time - 60
        self.request_history[account] = [
            ts for ts in self.request_history[account] 
            if ts > cutoff_time
        ]
        
        if len(self.request_history[account]) >= self.requests_per_minute:
            oldest_request = self.request_history[account][0]
            wait_time = (oldest_request + 60 - current_time)
            if wait_time > 0:
                logger.warning(
                    f"{self.logger_prefix} [{account}] Rate limit! "
                    f"({self.requests_per_minute}/min) ⏳ {wait_time:.2f}s..."
                )
                await asyncio.sleep(wait_time)
                current_time = time.time()
        
        self.last_request[account] = current_time
        self.request_history[account].append(current_time)
        
        return current_time
    
    def get_remaining_time(self, account: str) -> float:
        """Lấy thời gian phải chờ để gửi request tiếp theo"""
        if account not in self.last_request:
            return 0
        
        elapsed = time.time() - self.last_request[account]
        remaining = max(0, self.min_delay - elapsed)
        return remaining
    
    def get_stats(self, account: str) -> dict:
        """Lấy thống kê rate limiter"""
        history = self.request_history.get(account, [])
        current_time = time.time()
        
        recent = len([ts for ts in history if ts > current_time - 60])
        
        return {
            'last_request': self.last_request.get(account),
            'requests_last_minute': recent,
            'remaining_time': self.get_remaining_time(account),
            'utilization': f"{(recent/self.requests_per_minute*100):.1f}%"
        }


class BurstLimiter:
    """Giới hạn burst (spike) requests"""
    
    def __init__(self, max_burst: int = 5, window_seconds: int = 10):
        self.max_burst = max_burst
        self.window_seconds = window_seconds
        self.request_times = {}
    
    async def wait_if_burst(self, account: str) -> bool:
        """Kiểm tra và chờ nếu exceed burst limit"""
        current_time = time.time()
        
        if account not in self.request_times:
            self.request_times[account] = []
        
        cutoff_time = current_time - self.window_seconds
        self.request_times[account] = [
            ts for ts in self.request_times[account] 
            if ts > cutoff_time
        ]
        
        if len(self.request_times[account]) >= self.max_burst:
            oldest_time = self.request_times[account][0]
            wait_time = (oldest_time + self.window_seconds - current_time)
            
            if wait_time > 0:
                logger.warning(
                    f"🔥 Phát hiện Burst! ({self.max_burst} trong {self.window_seconds}s) "
                    f"⏳ {wait_time:.2f}s..."
                )
                await asyncio.sleep(wait_time)
                return True
        
        self.request_times[account].append(time.time())
        return False


class SmartDelayInjector:
    """Smart delay injection"""
    
    def __init__(self, 
                 min_delay: float = 0.1,
                 max_delay: float = 0.5):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_action_time = {}
    
    async def inject_smart_delay(self, account: str = "", action_name: str = ""):
        """Inject smart delay dựa vào action type"""
        
        delays = {
            "fill_input": random.uniform(0.05, 0.15),
            "click_button": random.uniform(0.1, 0.3),
            "submit": random.uniform(0.2, 0.5),
            "scroll": random.uniform(0.1, 0.2),
            "wait_result": random.uniform(1.0, 2.0),
        }
        
        delay = delays.get(action_name, random.uniform(self.min_delay, self.max_delay))
        
        if action_name == "wait_result":
            logger.debug(f"⏳ {action_name}: {delay:.2f}s")
        else:
            logger.debug(f"⏳ {action_name}: {delay*1000:.0f}ms") if delay < 1 else logger.debug(f"⏳ {action_name}: {delay:.2f}s")
        
        await asyncio.sleep(delay)
    
    async def inject_human_like_behavior(self):
        """Simulate human-like behavior"""
        if random.random() < 0.3:
            delay = random.uniform(0.5, 1.5)
            logger.debug(f"🎭 Tạm dừng hành động con người: {delay:.2f}s")
            await asyncio.sleep(delay)


class AntiDetectionManager:
    """Quản lý anti-detection strategies"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(
            min_delay=0.8,
            requests_per_minute=30
        )
        self.burst_limiter = BurstLimiter(max_burst=5, window_seconds=10)
        self.delay_injector = SmartDelayInjector(min_delay=0.1, max_delay=0.5)
        self.last_status_check = {}
        self.logger_prefix = "🛡️ ANTI-DETECTION"
    
    async def apply_all_protections(self, account: str):
        """Apply tất cả protections"""
        await self.rate_limiter.wait_if_needed(account)
        is_burst = await self.burst_limiter.wait_if_burst(account)
        
        if is_burst or random.random() < 0.2:
            await self.delay_injector.inject_smart_delay(account, "submit")
    
    async def check_account_health(self, account: str, browser_context) -> bool:
        """Kiểm tra tài khoản còn khỏe không"""
        try:
            page = await browser_context.new_page()
            await page.goto("https://www.google.com", timeout=5000)
            
            title = await page.title()
            await page.close()
            
            self.last_status_check[account] = datetime.now()
            is_healthy = "google" in title.lower()
            
            if is_healthy:
                logger.info(f"{self.logger_prefix} [{account}] ✅ Khỏe")
            else:
                logger.warning(f"{self.logger_prefix} [{account}] ⚠️ Trạng thái không xác định")
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"{self.logger_prefix} [{account}] ❌ Kiểm tra sức khỏe thất bại: {e}")
            return False
    
    def print_stats(self):
        """In thống kê anti-detection"""
        logger.info("\n" + "="*70)
        logger.info(f"{self.logger_prefix} THỐNG KÊ:")
        
        for account in self.rate_limiter.last_request.keys():
            stats = self.rate_limiter.get_stats(account)
            logger.info(
                f"  [{account}] "
                f"Requests/min: {stats['requests_last_minute']}/{self.rate_limiter.requests_per_minute} "
                f"({stats['utilization']}) | "
                f"Còn lại: {stats['remaining_time']:.2f}s"
            )
        
        logger.info("="*70 + "\n")


# Global anti-detection manager
anti_detection = None

def init_anti_detection() -> AntiDetectionManager:
    """Khởi tạo anti-detection"""
    global anti_detection
    anti_detection = AntiDetectionManager()
    logger.info("✅ Anti-Detection khởi tạo xong (v3.6 OPTIMIZED)")
    return anti_detection

def get_anti_detection() -> AntiDetectionManager:
    """Lấy anti-detection instance"""
    global anti_detection
    if anti_detection is None:
        anti_detection = init_anti_detection()
    return anti_detection
