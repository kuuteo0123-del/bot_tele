"""
🔗 CDP CONNECTOR - Smart CDP connection with health checks (FIX #1)
"""

import socket
import asyncio
from logger_setup import logger
from config import Config

class CDPConnector:
    """Handle CDP connection with retry logic"""
    
    @staticmethod
    def check_port_availability(host: str, port: int, timeout: int = None) -> bool:
        """Check if port is available"""
        if timeout is None:
            timeout = Config.CDP_TIMEOUT
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            is_available = result == 0
            
            if is_available:
                logger.debug(f"✅ CDP port {host}:{port} is available")
            else:
                logger.warning(f"❌ CDP port {host}:{port} is NOT available")
            
            return is_available
        
        except Exception as e:
            logger.warning(f"⚠️ Error checking port {host}:{port}: {e}")
            return False
    
    @staticmethod
    async def connect_to_cdp(playwright_instance, max_retries: int = None):
        """Connect to CDP with retry logic"""
        
        if max_retries is None:
            max_retries = Config.CDP_RETRY_ATTEMPTS
        
        cdp_url = f"http://{Config.CDP_HOST}:{Config.CDP_PORT}"
        
        logger.info(f"\n🔗 Attempting to connect to CDP: {cdp_url}")
        
        # First check port availability
        if not CDPConnector.check_port_availability(Config.CDP_HOST, Config.CDP_PORT):
            logger.error(f"❌ CDP port {Config.CDP_PORT} is not responding!")
            logger.info("   Make sure you have run: python manual_browser.py")
            logger.info(f"   Expected CDP at: {cdp_url}")
            return None
        
        # Try to connect with retries
        for attempt in range(max_retries):
            try:
                logger.info(f"   Attempt {attempt + 1}/{max_retries}...")
                
                context = await asyncio.wait_for(
                    playwright_instance.firefox.connect_over_cdp(cdp_url),
                    timeout=Config.CDP_TIMEOUT
                )
                
                logger.info(f"✅ Connected to CDP successfully!")
                return context
            
            except asyncio.TimeoutError:
                logger.warning(f"⚠️ Timeout connecting to CDP (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
            
            except ConnectionRefusedError:
                logger.warning(f"⚠️ Connection refused (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
            
            except Exception as e:
                logger.warning(f"⚠️ Error connecting to CDP: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
        
        logger.error(f"❌ Failed to connect to CDP after {max_retries} attempts")
        logger.error(f"   Please ensure: python manual_browser.py is running")
        logger.error(f"   CDP Address: {cdp_url}")
        return None

def get_cdp_connector():
    """Get CDP connector instance"""
    return CDPConnector()
