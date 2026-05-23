"""
📦 BATCH PROCESSOR - Process multiple codes efficiently (FIX #7)
"""

import asyncio
import time
from logger_setup import logger
from config import Config

class BatchSubmissionProcessor:
    """Process multiple submissions in batches"""
    
    def __init__(self, batch_size: int = None, wait_time: float = None):
        self.batch_size = batch_size or Config.BATCH_SIZE
        self.wait_time = wait_time or Config.BATCH_WAIT_TIME
        self.pending_tasks = []
        self.batch_count = 0
    
    def add_task(self, task):
        """Add task to batch"""
        self.pending_tasks.append(task)
        logger.debug(f"   📦 Added to batch ({len(self.pending_tasks)}/{self.batch_size})")
    
    async def flush(self):
        """Execute pending tasks in batch"""
        if not self.pending_tasks:
            return []
        
        batch_id = self.batch_count
        self.batch_count += 1
        
        logger.info(f"\n🚀 Batch #{batch_id}: Processing {len(self.pending_tasks)} tasks")
        
        start_time = time.time()
        
        try:
            results = await asyncio.gather(*self.pending_tasks, return_exceptions=True)
            
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
            failure_count = len(self.pending_tasks) - success_count
            
            duration = time.time() - start_time
            
            logger.info(f"✅ Batch #{batch_id} completed in {duration:.2f}s")
            logger.info(f"   ✅ Success: {success_count} | ❌ Failed: {failure_count}")
            
            self.pending_tasks = []
            return results
        
        except Exception as e:
            logger.error(f"❌ Batch #{batch_id} error: {e}")
            self.pending_tasks = []
            return []
    
    async def add_and_auto_flush(self, task):
        """Add task and auto-flush if batch is full"""
        self.add_task(task)
        
        if len(self.pending_tasks) >= self.batch_size:
            return await self.flush()
        
        return []
    
    def is_full(self) -> bool:
        """Check if batch is full"""
        return len(self.pending_tasks) >= self.batch_size
    
    def get_pending_count(self) -> int:
        """Get number of pending tasks"""
        return len(self.pending_tasks)
    
    def get_stats(self) -> dict:
        """Get batch statistics"""
        return {
            'batch_count': self.batch_count,
            'pending_tasks': len(self.pending_tasks),
            'batch_size': self.batch_size
        }

_batch_processor = None

def init_batch_processor():
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchSubmissionProcessor()
    return _batch_processor

def get_batch_processor():
    return init_batch_processor()

async def process_codes_in_batch(codes: list, accounts: list, submit_func, systems: dict) -> list:
    """Process codes in batches efficiently"""
    
    if not Config.BATCH_MODE_ENABLED:
        logger.info("📋 Batch mode disabled, processing sequentially")
        return await process_sequentially(codes, accounts, submit_func, systems)
    
    logger.info(f"\n📦 Batch Processing: {len(codes)} codes, {len(accounts)} accounts")
    
    processor = get_batch_processor()
    all_results = []
    
    for i, code in enumerate(codes):
        if i < len(accounts):
            account = accounts[i]
            task = submit_func(account["username"], code, systems)
            await processor.add_and_auto_flush(task)
    
    if processor.get_pending_count() > 0:
        final_results = await processor.flush()
        all_results.extend(final_results)
    
    return all_results

async def process_sequentially(codes: list, accounts: list, submit_func, systems: dict) -> list:
    """Process codes sequentially (fallback)"""
    
    logger.info(f"\n📋 Sequential Processing: {len(codes)} codes, {len(accounts)} accounts")
    
    all_results = []
    
    for i, code in enumerate(codes):
        if i < len(accounts):
            account = accounts[i]
            
            try:
                result = await submit_func(account["username"], code, systems)
                all_results.append(result)
            
            except Exception as e:
                logger.error(f"❌ Error processing code {i+1}: {e}")
                all_results.append({'success': False, 'error': str(e)})
    
    return all_results
