"""
📄 PAGE LOADER - Load pages with retry logic and timeout handling (FIX #4)
"""

import asyncio
import random
import time
from logger_setup import logger
from config import Config

class PageLoader:
    """Load pages with retry logic"""
    
    @staticmethod
    async def load_page_with_retry(page, url: str, user: str, max_retries: int = None) -> bool:
        """Load page with retry logic"""
        
        if max_retries is None:
            max_retries = Config.PAGE_LOAD_MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🌐 [{user}] Loading: {url} (attempt {attempt + 1}/{max_retries})")
                
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                await asyncio.wait_for(
                    page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=Config.PAGE_LOAD_TIMEOUT
                    ),
                    timeout=Config.PAGE_LOAD_TIMEOUT / 1000
                )
                
                try:
                    await asyncio.wait_for(
                        page.wait_for_load_state("networkidle", timeout=5000),
                        timeout=5
                    )
                except:
                    logger.debug(f"   ⚠️ Network idle timeout (acceptable)")
                
                await asyncio.sleep(1.0)
                
                logger.info(f"✅ [{user}] Page loaded successfully")
                return True
            
            except asyncio.TimeoutError:
                logger.warning(f"⏱️  [{user}] Load timeout (attempt {attempt + 1}/{max_retries})")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(Config.PAGE_LOAD_RETRY_DELAY)
                else:
                    logger.error(f"❌ [{user}] Failed to load page after {max_retries} attempts")
                    return False
            
            except Exception as e:
                logger.warning(f"⚠️  [{user}] Load error (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    try:
                        logger.debug(f"   🔄 Attempting reload...")
                        await page.reload(wait_until="domcontentloaded", timeout=10000)
                    except:
                        pass
                    
                    await asyncio.sleep(Config.PAGE_LOAD_RETRY_DELAY)
                else:
                    logger.error(f"❌ [{user}] Failed to load page after {max_retries} attempts")
                    return False
        
        return False
    
    @staticmethod
    async def wait_for_element(page, selector: str, timeout_ms: int = 5000) -> bool:
        """Wait for element to appear"""
        try:
            await asyncio.wait_for(
                page.wait_for_selector(selector, timeout=timeout_ms),
                timeout=timeout_ms / 1000
            )
            return True
        except:
            return False

def get_page_loader():
    """Get page loader instance"""
    return PageLoader()
