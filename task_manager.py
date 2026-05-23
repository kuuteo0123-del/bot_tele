"""
📋 TASK MANAGER & QUEUE SYSTEM
Quản lý task, priority queue, scheduling
"""

import asyncio
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from logger_setup import logger


class TaskPriority(Enum):
    """Mức ưu tiên task"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class TaskStatus(Enum):
    """Trạng thái task"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


@dataclass
class CodeTask:
    """Một task gửi code"""
    code: str
    channel_id: int
    account_username: str
    target_url: str
    priority: TaskPriority = TaskPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 2
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    
    def __lt__(self, other):
        """So sánh priority (cho PriorityQueue)"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at
    
    def mark_started(self):
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
    
    def mark_success(self, result: str):
        self.status = TaskStatus.SUCCESS
        self.completed_at = datetime.now()
        self.result = result
    
    def mark_failed(self, error: str):
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
    
    def mark_retrying(self):
        self.status = TaskStatus.RETRYING
        self.retry_count += 1
    
    def get_duration(self) -> Optional[float]:
        """Tính thời gian chạy (giây)"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def __repr__(self):
        return (f"CodeTask(code={self.code}, account={self.account_username}, "
                f"status={self.status.value}, priority={self.priority.name})")


class TaskQueue:
    """Priority queue quản lý tasks"""
    
    def __init__(self, max_concurrent: int = 3):
        self.queue = asyncio.PriorityQueue()
        self.task_history: List[CodeTask] = []
        self.running_tasks: dict = {}
        self.max_concurrent = max_concurrent
        self.running_count = 0
        self.lock = asyncio.Lock()
    
    async def add_task(self, task: CodeTask):
        """Thêm task vào queue"""
        await self.queue.put((task.priority.value, id(task), task))
        logger.info(
            f"📋 Task thêm: {task.code} | Account: {task.account_username} | "
            f"Priority: {task.priority.name} | Queue size: {self.queue.qsize()}"
        )
    
    async def get_next_task(self) -> Optional[CodeTask]:
        """Lấy task tiếp theo"""
        if self.queue.empty():
            return None
        
        try:
            _, _, task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            return task
        except asyncio.TimeoutError:
            return None
    
    async def can_execute_task(self) -> bool:
        """Kiểm tra có thể chạy task không"""
        async with self.lock:
            if self.running_count < self.max_concurrent:
                self.running_count += 1
                return True
            return False
    
    async def execute_task(self, task: CodeTask, executor: Callable):
        """Chạy 1 task"""
        try:
            task.mark_started()
            
            result = await executor(task)
            
            if result.get('success'):
                task.mark_success(result.get('message', 'Thành công'))
                logger.info(f"✅ Task thành công: {task.code}")
            else:
                if task.retry_count < task.max_retries:
                    task.mark_retrying()
                    logger.warning(f"🔄 Task retry: {task.code} ({task.retry_count}/{task.max_retries})")
                    await self.add_task(task)
                else:
                    task.mark_failed(result.get('message', 'Thất bại'))
                    logger.error(f"❌ Task thất bại: {task.code}")
        
        except Exception as e:
            if task.retry_count < task.max_retries:
                task.mark_retrying()
                logger.warning(f"🔄 Task retry do lỗi: {task.code}")
                await self.add_task(task)
            else:
                task.mark_failed(str(e))
                logger.error(f"❌ Task lỗi: {task.code} - {e}")
        
        finally:
            async with self.lock:
                self.task_history.append(task)
                self.running_count -= 1
    
    def get_stats(self) -> dict:
        """Lấy thống kê queue"""
        total = len(self.task_history)
        success = sum(1 for t in self.task_history if t.status == TaskStatus.SUCCESS)
        failed = sum(1 for t in self.task_history if t.status == TaskStatus.FAILED)
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'pending': self.queue.qsize(),
            'running': self.running_count,
            'success_rate': f"{(success/total*100):.1f}%" if total > 0 else "N/A"
        }
    
    def get_account_stats(self, account: str) -> dict:
        """Lấy stats cho 1 account"""
        tasks = [t for t in self.task_history if t.account_username == account]
        success = sum(1 for t in tasks if t.status == TaskStatus.SUCCESS)
        failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)
        total = len(tasks)
        
        return {
            'account': account,
            'total': total,
            'success': success,
            'failed': failed,
            'success_rate': f"{(success/total*100):.1f}%" if total > 0 else "N/A"
        }
    
    def print_stats(self):
        """In thống kê"""
        stats = self.get_stats()
        
        logger.info("\n" + "="*70)
        logger.info("📊 THỐNG KÊ TASK QUEUE:")
        logger.info(f"   ✅ Thành công: {stats['success']}")
        logger.info(f"   ❌ Thất bại: {stats['failed']}")
        logger.info(f"   ⏳ Đang chờ: {stats['pending']}")
        logger.info(f"   🔄 Đang chạy: {stats['running']}")
        logger.info(f"   📈 Tỉ lệ thành công: {stats['success_rate']}")
        logger.info(f"   Tổng: {stats['total']}")
        
        logger.info("\n📱 ACCOUNT STATS:")
        accounts = set(t.account_username for t in self.task_history)
        for account in sorted(accounts):
            acc_stats = self.get_account_stats(account)
            logger.info(
                f"   {account}: "
                f"✅ {acc_stats['success']} | "
                f"❌ {acc_stats['failed']} | "
                f"Tỉ lệ: {acc_stats['success_rate']}"
            )
        
        logger.info("="*70 + "\n")


class Scheduler:
    """Simple scheduler cho recurring tasks"""
    
    def __init__(self):
        self.scheduled_tasks = []
        self.is_running = False
    
    def schedule_at(self, when: datetime, func: Callable, *args, **kwargs):
        """Schedule task ở thời điểm cụ thể"""
        self.scheduled_tasks.append({
            'when': when,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'executed': False
        })
    
    def schedule_every(self, hours: int, func: Callable, *args, **kwargs):
        """Schedule task mỗi X giờ"""
        task = {
            'interval_hours': hours,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'last_execution': None
        }
        self.scheduled_tasks.append(task)
    
    async def start(self):
        """Start scheduler"""
        self.is_running = True
        logger.info("🕐 Scheduler bắt đầu")
        
        while self.is_running:
            current_time = datetime.now()
            
            for task in self.scheduled_tasks:
                try:
                    if 'when' in task:
                        if not task['executed'] and current_time >= task['when']:
                            logger.info(f"⏰ Chạy scheduled task: {task['func'].__name__}")
                            await task['func'](*task['args'], **task['kwargs'])
                            task['executed'] = True
                    
                    elif 'interval_hours' in task:
                        last = task['last_execution']
                        if last is None or (current_time - last).total_seconds() >= task['interval_hours'] * 3600:
                            logger.info(f"⏰ Chạy recurring task: {task['func'].__name__}")
                            await task['func'](*task['args'], **task['kwargs'])
                            task['last_execution'] = current_time
                
                except Exception as e:
                    logger.error(f"❌ Scheduler lỗi: {e}")
            
            await asyncio.sleep(60)
    
    def stop(self):
        self.is_running = False
        logger.info("🛑 Scheduler dừng")


# Global instances
task_queue = None
scheduler = None

def init_task_system(max_concurrent: int = 3) -> tuple:
    """Khởi tạo task system"""
    global task_queue, scheduler
    
    task_queue = TaskQueue(max_concurrent=max_concurrent)
    scheduler = Scheduler()
    
    return task_queue, scheduler

def get_task_queue() -> TaskQueue:
    """Lấy task queue"""
    global task_queue
    if task_queue is None:
        init_task_system()
    return task_queue

def get_scheduler() -> Scheduler:
    """Lấy scheduler"""
    global scheduler
    if scheduler is None:
        init_task_system()
    return scheduler
