"""ุ
⚙️ TASK MANAGER - Quản lý tasks concurrency
"""

import asyncio
from enum import Enum
from datetime import datetime
from logger_setup import logger

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 3
    NORMAL = 2
    HIGH = 1

class CodeTask:
    """Task object"""
    
    def __init__(self, code: str, username: str, url: str, priority: TaskPriority = TaskPriority.NORMAL):
        self.code = code
        self.username = username
        self.url = url
        self.priority = priority
        self.created_at = datetime.now()
        self.status = "pending"
    
    def __lt__(self, other):
        """For priority queue"""
        return self.priority.value < other.priority.value

class TaskScheduler:
    """Task scheduler - quản lý concurrent tasks"""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.task_queue = asyncio.PriorityQueue()
        self.active_tasks = 0
        self.completed = 0
        self.failed = 0
    
    async def add_task(self, task: CodeTask):
        """Thêm task"""
        await self.task_queue.put((task.priority.value, task))
        logger.debug(f"📝 Task added: {task.code}")
    
    async def process_tasks(self, worker_func):
        """Process tasks"""
        workers = [
            asyncio.create_task(self._worker(worker_func))
            for _ in range(self.max_concurrent)
        ]
        
        await asyncio.gather(*workers)
    
    async def _worker(self, worker_func):
        """Worker - xử lý tasks"""
        while True:
            try:
                _, task = await asyncio.wait_for(self.task_queue.get(), timeout=1)
                
                self.active_tasks += 1
                logger.debug(f"⚙️ Processing: {task.code}")
                
                try:
                    result = await worker_func(task)
                    if result:
                        self.completed += 1
                    else:
                        self.failed += 1
                except Exception as e:
                    logger.error(f"❌ Task error: {e}")
                    self.failed += 1
                finally:
                    self.active_tasks -= 1
                    self.task_queue.task_done()
            
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"❌ Worker error: {e}")
                break
    
    def get_stats(self) -> dict:
        """Lấy thống kê"""
        return {
            'active': self.active_tasks,
            'completed': self.completed,
            'failed': self.failed,
            'total': self.completed + self.failed,
            'queue_size': self.task_queue.qsize()
        }

# Global instances
_task_scheduler = None

def init_task_system(max_concurrent: int = 3):
    global _task_scheduler
    if _task_scheduler is None:
        _task_scheduler = TaskScheduler(max_concurrent)
    return _task_scheduler, None

def get_task_scheduler() -> TaskScheduler:
    global _task_scheduler
    if _task_scheduler is None:
        init_task_system()
    return _task_scheduler
