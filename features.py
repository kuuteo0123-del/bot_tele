"""ุ
✨ FEATURES - Advanced features & utilities
"""

import sys
import signal
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from logger_setup import logger
from config import Config

def print_version_info():
    """In thông tin version"""
    logger.info("\n" + "="*70)
    logger.info("🤖 BOT SĂN CODE v3.9 - ADVANCED")
    logger.info("="*70)
    logger.info(f"🎯 Browser: Firefox (Persistent Profiles)")
    logger.info(f"📊 Viewport: {Config.VIEWPORT_WIDTH}x{Config.VIEWPORT_HEIGHT}")
    logger.info(f"⏱️ Build: 2026-05-23")
    logger.info(f"📁 Profiles: {Config.BROWSER_PROFILE_DIR}")
    logger.info("="*70 + "\n")

class ConfigValidator:
    """Validate config"""
    
    @staticmethod
    def validate():
        """Validate cấu hình"""
        errors = []
        
        if not Config.API_ID or not Config.API_HASH:
            errors.append("❌ API_ID hoặc API_HASH chưa cấu hình")
        
        if not Config.CHANNEL_CONFIG:
            errors.append("❌ CHANNEL_CONFIG chưa cấu hình")
        
        if errors:
            for err in errors:
                logger.error(err)
            return False
        
        logger.info("✅ Config hợp lệ")
        return True

class StatsManager:
    """Stats manager"""
    
    def __init__(self):
        self.submissions = 0
        self.successes = 0
        self.failures = 0
    
    def record_submission(self, success: bool):
        self.submissions += 1
        if success:
            self.successes += 1
        else:
            self.failures += 1
    
    def get_stats(self) -> dict:
        return {
            'submissions': self.submissions,
            'successes': self.successes,
            'failures': self.failures,
            'success_rate': (self.successes / self.submissions * 100) if self.submissions > 0 else 0
        }

class MemoryMonitor:
    """Memory monitor"""
    
    def __init__(self, max_memory_mb: int = 500):
        self.max_memory_mb = max_memory_mb
    
    def check_memory(self) -> dict:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        return {
            'memory_mb': memory_mb,
            'max_memory_mb': self.max_memory_mb,
            'exceeded': memory_mb > self.max_memory_mb
        }

class GracefulShutdownHandler:
    """Handle graceful shutdown"""
    
    def __init__(self):
        self.bot_state = None
        self.is_shutting_down = False
    
    def setup(self, bot_state):
        self.bot_state = bot_state
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        if self.is_shutting_down:
            logger.warning("⚠️ Forced shutdown")
            sys.exit(1)
        
        self.is_shutting_down = True
        logger.info("🛑 Graceful shutdown...")
        if self.bot_state:
            self.bot_state.is_running = False

class DatabaseBackup:
    """Database backup"""
    
    @staticmethod
    async def schedule_daily_backup(db_path: str, bot_state):
        import asyncio
        from shutil import copy
        
        while bot_state.is_running:
            try:
                backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d')}"
                if Path(db_path).exists():
                    copy(db_path, backup_path)
                    logger.info(f"✅ Database backup: {backup_path}")
            except Exception as e:
                logger.error(f"❌ Backup error: {e}")
            
            await asyncio.sleep(86400)  # 24 hours

class ProfileCleaner:
    """Profile cleaner"""
    
    @staticmethod
    async def schedule_daily_cleanup(profile_dir: Path, bot_state):
        import asyncio
        
        while bot_state.is_running:
            try:
                if not profile_dir.exists():
                    await asyncio.sleep(86400)
                    continue
                
                cleanup_days = Config.PROFILE_CLEANUP_DAYS
                cutoff_time = datetime.now() - timedelta(days=cleanup_days)
                
                deleted_count = 0
                for profile_path in profile_dir.iterdir():
                    if not profile_path.is_dir():
                        continue
                    
                    mtime = datetime.fromtimestamp(profile_path.stat().st_mtime)
                    if mtime < cutoff_time:
                        shutil.rmtree(profile_path)
                        deleted_count += 1
                
                if deleted_count > 0:
                    logger.info(f"🧹 Deleted {deleted_count} old profiles")
            
            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
            
            await asyncio.sleep(86400)  # 24 hours

class SystemTester:
    """Test system setup"""
    
    def __init__(self, client):
        self.client = client
    
    async def test_all(self, db):
        """Test all systems"""
        logger.info("\n" + "="*70)
        logger.info("🧪 SYSTEM TEST")
        logger.info("="*70)
        
        # Test Telegram
        try:
            me = await self.client.get_me()
            logger.info(f"✅ Telegram: OK (@{me.username})")
        except Exception as e:
            logger.error(f"❌ Telegram: {e}")
            return False
        
        # Test Database
        try:
            stats = db.get_statistics()
            logger.info(f"✅ Database: OK (submissions: {stats.get('total', 0)})")
        except Exception as e:
            logger.error(f"❌ Database: {e}")
            return False
        
        logger.info("="*70 + "\n")
        return True

# Global instances
_stats_manager = None
_submission_logger = None
_memory_monitor = None
_shutdown_handler = None
_db_backup = None
_profile_cleaner = None
_system_tester = None

def get_stats_manager() -> StatsManager:
    global _stats_manager
    if _stats_manager is None:
        _stats_manager = StatsManager()
    return _stats_manager

def get_submission_logger():
    return None

def get_memory_monitor() -> MemoryMonitor:
    global _memory_monitor
    if _memory_monitor is None:
        _memory_monitor = MemoryMonitor()
    return _memory_monitor

def get_shutdown_handler() -> GracefulShutdownHandler:
    global _shutdown_handler
    if _shutdown_handler is None:
        _shutdown_handler = GracefulShutdownHandler()
    return _shutdown_handler

def get_db_backup() -> DatabaseBackup:
    global _db_backup
    if _db_backup is None:
        _db_backup = DatabaseBackup()
    return _db_backup

def get_profile_cleaner() -> ProfileCleaner:
    global _profile_cleaner
    if _profile_cleaner is None:
        _profile_cleaner = ProfileCleaner()
    return _profile_cleaner

def get_system_tester(client) -> SystemTester:
    global _system_tester
    if _system_tester is None:
        _system_tester = SystemTester(client)
    return _system_tester
