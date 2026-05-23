"""
📊 PERFORMANCE PROFILER - Track & report performance metrics (FIX #8)
"""

import time
from datetime import datetime
from collections import defaultdict
from logger_setup import logger
from config import Config

class PerformanceMetric:
    """Single performance metric"""
    
    def __init__(self):
        self.times = []
        self.successes = 0
        self.failures = 0
        self.start_time = time.time()
    
    def record(self, duration: float, success: bool):
        """Record a metric"""
        self.times.append(duration)
        if success:
            self.successes += 1
        else:
            self.failures += 1
    
    def get_stats(self) -> dict:
        """Get statistics"""
        if not self.times:
            return {
                'count': 0,
                'avg_time': 0,
                'min_time': 0,
                'max_time': 0,
                'success_rate': 0
            }
        
        total = self.successes + self.failures
        return {
            'count': total,
            'avg_time': sum(self.times) / len(self.times),
            'min_time': min(self.times),
            'max_time': max(self.times),
            'success_rate': (self.successes / total * 100) if total > 0 else 0,
            'successes': self.successes,
            'failures': self.failures
        }

class PerformanceProfiler:
    """Track performance metrics across the system"""
    
    def __init__(self):
        self.metrics = defaultdict(PerformanceMetric)
        self.start_time = time.time()
    
    def record_metric(self, key: str, duration: float, success: bool):
        """Record a metric"""
        self.metrics[key].record(duration, success)
    
    def get_report(self) -> dict:
        """Generate performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - self.start_time,
            'metrics': {}
        }
        
        for key, metric in self.metrics.items():
            report['metrics'][key] = metric.get_stats()
        
        return report
    
    def print_report(self):
        """Print human-readable report"""
        report = self.get_report()
        
        logger.info("\n" + "="*70)
        logger.info("📊 PERFORMANCE REPORT")
        logger.info("="*70)
        logger.info(f"⏱️  Uptime: {report['uptime']:.0f}s")
        
        for key, stats in report['metrics'].items():
            if stats['count'] > 0:
                logger.info(f"\n📈 {key}:")
                logger.info(f"   Total: {stats['count']} | Success: {stats['successes']} | Failed: {stats['failures']}")
                logger.info(f"   Avg: {stats['avg_time']:.3f}s | Min: {stats['min_time']:.3f}s | Max: {stats['max_time']:.3f}s")
                logger.info(f"   Success Rate: {stats['success_rate']:.1f}%")
        
        logger.info("="*70 + "\n")
    
    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.start_time = time.time()
        logger.info("🔄 Performance metrics reset")

_profiler = None

def init_profiler():
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler

def get_profiler():
    return init_profiler()

async def periodic_report(bot_state):
    """Print periodic performance reports"""
    import asyncio
    
    logger.info("📊 Performance reporter started")
    profiler = get_profiler()
    
    while bot_state.is_running:
        try:
            await asyncio.sleep(Config.PERFORMANCE_REPORT_INTERVAL)
            
            if Config.PERFORMANCE_TRACKING_ENABLED:
                profiler.print_report()
        
        except Exception as e:
            logger.error(f"❌ Report error: {e}")
