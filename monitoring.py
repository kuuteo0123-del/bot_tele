"""ุ
📊 MONITORING - Monitor performance
"""

import time
from collections import defaultdict
from logger_setup import logger

class PerformanceMonitor:
    """Performance monitor"""
    
    def __init__(self):
        self.tasks = defaultdict(list)  # {task_name: [duration, duration, ...]}
    
    def record_task(self, task_name: str, duration: float, success: bool):
        """Record task"""
        self.tasks[task_name].append(duration)
        status = "✅" if success else "❌"
        logger.debug(f"{status} {task_name}: {duration:.2f}s")
    
    def get_stats(self, task_name: str = None) -> dict:
        """Get statistics"""
        if task_name:
            durations = self.tasks.get(task_name, [])
            if not durations:
                return {}
            
            return {
                'task': task_name,
                'count': len(durations),
                'avg': sum(durations) / len(durations),
                'min': min(durations),
                'max': max(durations)
            }
        
        return {task: self.get_stats(task) for task in self.tasks}

# Global instances
_health_monitor = None
_alert_manager = None
_perf_monitor = None

def init_monitoring():
    global _health_monitor, _alert_manager, _perf_monitor
    if _perf_monitor is None:
        _health_monitor = None
        _alert_manager = None
        _perf_monitor = PerformanceMonitor()
    return _health_monitor, _alert_manager, _perf_monitor

def get_monitoring_system():
    return init_monitoring()
