"""
📊 MONITORING & HEALTH SYSTEM
Giám sát sức khỏe hệ thống, performance tracking, alerts
"""

import asyncio
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from logger_setup import logger


class HealthMetrics:
    """Metrics để giám sát"""
    
    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.memory_mb = 0
        self.firefox_instances = 0
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return (f"HealthMetrics(CPU: {self.cpu_usage:.1f}%, "
                f"Memory: {self.memory_usage:.1f}% ({self.memory_mb}MB), "
                f"Firefox: {self.firefox_instances})")


class HealthMonitor:
    """Giám sát sức khỏe hệ thống"""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.metrics_history: List[HealthMetrics] = []
        self.is_running = False
        self.alerts = []
        
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.firefox_threshold = 10
    
    def get_current_metrics(self) -> HealthMetrics:
        """Lấy metrics hiện tại"""
        metrics = HealthMetrics()
        
        metrics.cpu_usage = psutil.cpu_percent(interval=1)
        
        memory = psutil.virtual_memory()
        metrics.memory_usage = memory.percent
        metrics.memory_mb = memory.used // (1024 * 1024)
        
        try:
            for proc in psutil.process_iter(['name']):
                if 'firefox' in proc.info['name'].lower():
                    metrics.firefox_instances += 1
        except:
            pass
        
        metrics.timestamp = datetime.now()
        return metrics
    
    def add_metrics(self, metrics: HealthMetrics):
        """Thêm metrics vào history"""
        self.metrics_history.append(metrics)
        
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    async def check_health(self) -> Dict:
        """Kiểm tra sức khỏe hệ thống"""
        metrics = self.get_current_metrics()
        self.add_metrics(metrics)
        
        status = "HEALTHY"
        warnings = []
        
        if metrics.cpu_usage > self.cpu_threshold:
            status = "DEGRADED"
            warnings.append(f"CPU cao: {metrics.cpu_usage:.1f}%")
        
        if metrics.memory_usage > self.memory_threshold:
            status = "DEGRADED"
            warnings.append(f"Memory cao: {metrics.memory_usage:.1f}% ({metrics.memory_mb}MB)")
        
        if metrics.firefox_instances > self.firefox_threshold:
            warnings.append(f"Firefox instances quá nhiều: {metrics.firefox_instances}")
        
        return {
            'status': status,
            'metrics': metrics,
            'warnings': warnings
        }
    
    async def start(self):
        """Bắt đầu monitoring"""
        self.is_running = True
        logger.info("🏥 Health Monitor bắt đầu")
        
        while self.is_running:
            try:
                health = await self.check_health()
                
                if health['warnings']:
                    for warning in health['warnings']:
                        logger.warning(f"⚠️ {warning}")
                
            except Exception as e:
                logger.error(f"❌ Lỗi kiểm tra sức khỏe: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Dừng monitoring"""
        self.is_running = False
        logger.info("🛑 Health Monitor dừng")
    
    def get_average_metrics(self, minutes: int = 5) -> Dict:
        """Lấy average metrics trong N phút"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent = [m for m in self.metrics_history if m.timestamp > cutoff_time]
        
        if not recent:
            return {}
        
        avg_cpu = sum(m.cpu_usage for m in recent) / len(recent)
        avg_memory = sum(m.memory_usage for m in recent) / len(recent)
        avg_firefox = sum(m.firefox_instances for m in recent) / len(recent)
        
        return {
            'avg_cpu': avg_cpu,
            'avg_memory': avg_memory,
            'avg_firefox': int(avg_firefox),
            'sample_count': len(recent)
        }


class Alert:
    """Một alert"""
    
    def __init__(self, level: str, message: str, context: Dict = None):
        self.level = level
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.now()
        self.resolved = False
        self.resolved_at = None
    
    def resolve(self):
        """Resolve alert"""
        self.resolved = True
        self.resolved_at = datetime.now()
    
    def __repr__(self):
        return f"Alert({self.level}: {self.message} @ {self.timestamp.strftime('%H:%M:%S')})"


class AlertManager:
    """Quản lý alerts"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}
    
    def add_alert(self, level: str, message: str, context: Dict = None) -> Alert:
        """Thêm alert"""
        alert = Alert(level, message, context)
        self.alerts.append(alert)
        
        if level in ['WARNING', 'ERROR', 'CRITICAL']:
            self.active_alerts[message] = alert
        
        emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🔴'
        }.get(level, '📢')
        
        logger.info(f"{emoji} {level}: {message}")
        
        return alert
    
    def resolve_alert(self, message: str):
        """Resolve alert"""
        if message in self.active_alerts:
            alert = self.active_alerts[message]
            alert.resolve()
            del self.active_alerts[message]
            logger.info(f"✅ Alert đã resolve: {message}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Lấy tất cả active alerts"""
        return list(self.active_alerts.values())
    
    def get_recent_alerts(self, minutes: int = 60) -> List[Alert]:
        """Lấy alerts gần đây"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [a for a in self.alerts if a.timestamp > cutoff_time]
    
    def print_alerts(self):
        """In alerts"""
        active = self.get_active_alerts()
        
        if not active:
            logger.info("✅ Không có active alerts")
            return
        
        logger.info("\n" + "="*70)
        logger.info(f"🚨 ACTIVE ALERTS ({len(active)}):")
        
        for alert in active:
            duration = (datetime.now() - alert.timestamp).total_seconds()
            logger.info(f"   {alert.level}: {alert.message} ({duration:.0f}s ago)")
        
        logger.info("="*70 + "\n")


class PerformanceMonitor:
    """Giám sát performance"""
    
    def __init__(self):
        self.task_times: Dict[str, List[float]] = {}
        self.task_success: Dict[str, int] = {}
        self.task_failed: Dict[str, int] = {}
    
    def record_task(self, task_name: str, duration: float, success: bool = True):
        """Ghi lại duration của task"""
        if task_name not in self.task_times:
            self.task_times[task_name] = []
            self.task_success[task_name] = 0
            self.task_failed[task_name] = 0
        
        self.task_times[task_name].append(duration)
        
        if success:
            self.task_success[task_name] += 1
        else:
            self.task_failed[task_name] += 1
    
    def get_task_stats(self, task_name: str) -> Dict:
        """Lấy stats cho task"""
        if task_name not in self.task_times:
            return {}
        
        times = self.task_times[task_name]
        
        return {
            'task_name': task_name,
            'total': len(times),
            'success': self.task_success.get(task_name, 0),
            'failed': self.task_failed.get(task_name, 0),
            'avg_duration': sum(times) / len(times) if times else 0,
            'min_duration': min(times) if times else 0,
            'max_duration': max(times) if times else 0,
            'success_rate': (self.task_success.get(task_name, 0) / len(times) * 100) if times else 0
        }
    
    def print_stats(self):
        """In stats"""
        if not self.task_times:
            logger.info("ℹ️ Không có performance data")
            return
        
        logger.info("\n" + "="*70)
        logger.info("⚡ THỐNG KÊ PERFORMANCE:")
        
        for task_name in self.task_times.keys():
            stats = self.get_task_stats(task_name)
            logger.info(f"\n   📊 {task_name}:")
            logger.info(f"      Tổng: {stats['total']} | ✅ {stats['success']} | ❌ {stats['failed']}")
            logger.info(f"      Tỉ lệ thành công: {stats['success_rate']:.1f}%")
            logger.info(f"      Avg: {stats['avg_duration']:.2f}s | Min: {stats['min_duration']:.2f}s | Max: {stats['max_duration']:.2f}s")
        
        logger.info("="*70 + "\n")


class MonitoringSystem:
    """Hệ thống monitoring toàn bộ"""
    
    def __init__(self):
        self.health_monitor = HealthMonitor(check_interval=60)
        self.alert_manager = AlertManager()
        self.performance_monitor = PerformanceMonitor()
        self.is_running = False
    
    async def start(self):
        """Bắt đầu monitoring"""
        self.is_running = True
        logger.info("📡 Monitoring System bắt đầu")
        
        asyncio.create_task(self.health_monitor.start())
    
    def stop(self):
        """Dừng monitoring"""
        self.is_running = False
        self.health_monitor.stop()
        logger.info("📡 Monitoring System dừng")
    
    def print_full_status(self):
        """In full status"""
        logger.info("\n" + "="*70)
        logger.info("📊 TRẠNG THÁI HỆ THỐNG TOÀN BỘ:")
        
        metrics = self.health_monitor.get_current_metrics()
        logger.info(f"\n🏥 HEALTH:")
        logger.info(f"   CPU: {metrics.cpu_usage:.1f}%")
        logger.info(f"   Memory: {metrics.memory_usage:.1f}% ({metrics.memory_mb}MB)")
        logger.info(f"   Firefox Instances: {metrics.firefox_instances}")
        
        active_alerts = self.alert_manager.get_active_alerts()
        logger.info(f"\n🚨 ALERTS: {len(active_alerts)} active")
        if active_alerts:
            for alert in active_alerts:
                logger.info(f"   - {alert.level}: {alert.message}")
        
        logger.info(f"\n⚡ PERFORMANCE:")
        if self.performance_monitor.task_times:
            for task_name in self.performance_monitor.task_times.keys():
                stats = self.performance_monitor.get_task_stats(task_name)
                logger.info(f"   - {task_name}: {stats['success_rate']:.1f}% success rate")
        else:
            logger.info("   Chưa có dữ liệu")
        
        logger.info("="*70 + "\n")


# Global instances
monitoring_system = None

def init_monitoring() -> tuple:
    """Khởi tạo monitoring system"""
    global monitoring_system
    
    monitoring_system = MonitoringSystem()
    
    return (
        monitoring_system.health_monitor,
        monitoring_system.alert_manager,
        monitoring_system.performance_monitor
    )

def get_monitoring_system() -> MonitoringSystem:
    """Lấy monitoring system"""
    global monitoring_system
    if monitoring_system is None:
        init_monitoring()
    return monitoring_system

def get_health_monitor():
    """Lấy health monitor"""
    return get_monitoring_system().health_monitor

def get_alert_manager():
    """Lấy alert manager"""
    return get_monitoring_system().alert_manager

def get_performance_monitor():
    """Lấy performance monitor"""
    return get_monitoring_system().performance_monitor
