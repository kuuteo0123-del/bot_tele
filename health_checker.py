"""
🏥 HEALTH CHECKER - Monitor bot health & auto-recovery (FIX #6)
"""

import asyncio
import time
from logger_setup import logger
from config import Config

class HealthChecker:
    """Monitor browser health and auto-recover"""
    
    def __init__(self):
        self.last_check = {}
        self.failed_checks = {}
        self.recovery_attempts = {}
    
    async def check_browser_health(self, user: str, bot_state) -> bool:
        """Check if browser context is still healthy"""
        try:
            if user not in bot_state.account_contexts:
                logger.warning(f"⚠️ [{user}] No browser context found")
                return False
            
            context = bot_state.account_contexts[user]
            
            if not hasattr(context, 'pages'):
                logger.warning(f"⚠️ [{user}] Context has no pages attribute")
                return False
            
            try:
                pages = context.pages
                if not pages:
                    logger.warning(f"⚠️ [{user}] No active pages in context")
                    return False
                
                page = pages[0]
                try:
                    _ = page.url
                    logger.debug(f"✅ [{user}] Browser health: OK")
                    self.failed_checks[user] = 0
                    return True
                except Exception as e:
                    logger.warning(f"⚠️ [{user}] Page not responsive: {e}")
                    return False
            
            except Exception as e:
                logger.warning(f"⚠️ [{user}] Context check failed: {e}")
                return False
        
        except Exception as e:
            logger.error(f"❌ [{user}] Health check error: {e}")
            return False
    
    async def trigger_auto_recovery(self, user: str, bot_state):
        """Attempt to recover unhealthy browser"""
        if not Config.AUTO_RECOVERY_ENABLED:
            logger.warning(f"⚠️ [{user}] Auto-recovery disabled")
            return False
        
        try:
            recovery_count = self.recovery_attempts.get(user, 0)
            
            if recovery_count >= 3:
                logger.error(f"❌ [{user}] Max recovery attempts reached")
                return False
            
            logger.info(f"🔄 [{user}] Attempting recovery (attempt {recovery_count + 1}/3)...")
            
            bot_state.cf_verified[user] = False
            
            try:
                if user in bot_state.account_contexts:
                    context = bot_state.account_contexts[user]
                    for page in list(context.pages):
                        try:
                            await page.close()
                        except:
                            pass
                    await context.close()
                    del bot_state.account_contexts[user]
            except Exception as e:
                logger.debug(f"   ⚠️ Failed to close old context: {e}")
            
            self.recovery_attempts[user] = recovery_count + 1
            logger.info(f"✅ [{user}] Recovery initiated")
            return True
        
        except Exception as e:
            logger.error(f"❌ [{user}] Recovery failed: {e}")
            return False
    
    async def periodic_health_check(self, bot_state):
        """Run periodic health checks"""
        logger.info("🏥 Health checker started")
        
        while bot_state.is_running:
            try:
                if not Config.HEALTH_CHECK_ENABLED:
                    await asyncio.sleep(Config.HEALTH_CHECK_INTERVAL)
                    continue
                
                logger.debug("🔍 Running health checks...")
                
                unhealthy_users = []
                
                for user in list(bot_state.account_contexts.keys()):
                    try:
                        is_healthy = await self.check_browser_health(user, bot_state)
                        
                        if not is_healthy:
                            self.failed_checks[user] = self.failed_checks.get(user, 0) + 1
                            
                            if self.failed_checks[user] >= 2:
                                unhealthy_users.append(user)
                        else:
                            self.failed_checks[user] = 0
                    
                    except Exception as e:
                        logger.debug(f"   ⚠️ Error checking {user}: {e}")
                
                for user in unhealthy_users:
                    await self.trigger_auto_recovery(user, bot_state)
                
                await asyncio.sleep(Config.HEALTH_CHECK_INTERVAL)
            
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(Config.HEALTH_CHECK_INTERVAL)

_health_checker = None

def init_health_checker():
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker

def get_health_checker():
    return init_health_checker()
