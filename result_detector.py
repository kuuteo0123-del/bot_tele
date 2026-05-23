"""
🎯 RESULT DETECTOR - Advanced result detection with multiple methods (FIX #5)
"""

import asyncio
from datetime import datetime
from logger_setup import logger
from config import Config

class ResultDetector:
    """Detect submission results using multiple methods"""
    
    SUCCESS_KEYWORDS = [
        "THÀNH CÔNG", "SUCCESS", "OK", "CỘNG", "RECEIVED",
        "SUCCESSFUL", "APPROVED", "ACCEPTED", "COMPLETED",
        "CONGRATULATIONS", "CLAIM", "CLAIMED"
    ]
    
    FAILED_KEYWORDS = [
        "SAI", "LỖI", "ĐÃ SỬ", "HẾT HẠN", "KHÔNG", "FAILED",
        "ERROR", "INVALID", "EXPIRED", "ALREADY USED", "NOT FOUND",
        "INCORRECT", "WRONG", "CANNOT"
    ]
    
    SUCCESS_SELECTORS = [
        ".alert-success", "[class*='success']", "[class*='green']",
        ".swal2-success", ".toast-success", ".notification-success"
    ]
    
    ERROR_SELECTORS = [
        ".alert-danger", ".alert-error", "[class*='error']",
        "[class*='failed']", ".swal2-error", ".toast-error"
    ]
    
    @staticmethod
    async def detect_by_text(page, user: str) -> dict:
        """Detect result by text content (Method 1)"""
        result = {'method': 'text', 'detected': False, 'text': '', 'status': None}
        
        try:
            selectors = [
                ".swal2-html-container",
                ".swal2-title",
                ".modal-body",
                ".alert",
                ".message",
                "[class*='result']",
                "[class*='response']"
            ]
            
            for sel in selectors:
                try:
                    elems = await page.query_selector_all(sel)
                    for elem in elems:
                        try:
                            if await elem.is_visible():
                                text = await elem.inner_text()
                                if text and len(text.strip()) > 0:
                                    result['text'] = text.strip()
                                    result['detected'] = True
                                    
                                    text_upper = text.upper()
                                    
                                    if any(kw in text_upper for kw in ResultDetector.SUCCESS_KEYWORDS):
                                        result['status'] = 'SUCCESS'
                                        logger.debug(f"   ✅ Result by text (success): {text[:60]}")
                                        return result
                                    
                                    if any(kw in text_upper for kw in ResultDetector.FAILED_KEYWORDS):
                                        result['status'] = 'FAILED'
                                        logger.debug(f"   ❌ Result by text (failed): {text[:60]}")
                                        return result
                        except:
                            pass
                except:
                    pass
        
        except Exception as e:
            logger.debug(f"   ⚠️ Text detection error: {e}")
        
        return result
    
    @staticmethod
    async def detect_by_color(page, user: str) -> dict:
        """Detect result by CSS color/class (Method 2)"""
        result = {'method': 'color', 'detected': False, 'status': None}
        
        try:
            for sel in ResultDetector.SUCCESS_SELECTORS:
                try:
                    elem = await page.query_selector(sel)
                    if elem and await elem.is_visible():
                        result['detected'] = True
                        result['status'] = 'SUCCESS'
                        logger.debug(f"   ✅ Result by color (success): {sel}")
                        return result
                except:
                    pass
            
            for sel in ResultDetector.ERROR_SELECTORS:
                try:
                    elem = await page.query_selector(sel)
                    if elem and await elem.is_visible():
                        result['detected'] = True
                        result['status'] = 'FAILED'
                        logger.debug(f"   ❌ Result by color (failed): {sel}")
                        return result
                except:
                    pass
        
        except Exception as e:
            logger.debug(f"   ⚠️ Color detection error: {e}")
        
        return result
    
    @staticmethod
    async def detect_by_dom_change(page, user: str) -> dict:
        """Detect result by DOM changes (Method 3)"""
        result = {'method': 'dom', 'detected': False, 'status': None}
        
        try:
            disabled_inputs = await page.query_selector_all("input:disabled")
            if disabled_inputs:
                result['detected'] = True
                result['status'] = 'SUCCESS'
                logger.debug(f"   ✅ Result by DOM (form disabled)")
                return result
        
        except Exception as e:
            logger.debug(f"   ⚠️ DOM detection error: {e}")
        
        return result
    
    @staticmethod
    async def take_screenshot_for_debug(page, user: str) -> dict:
        """Take screenshot for manual review (Method 4)"""
        result = {'method': 'screenshot', 'detected': False, 'screenshot_path': None}
        
        try:
            if Config.SCREENSHOT_ON_UNKNOWN:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"logs/unknown_result_{user}_{timestamp}.png"
                
                await page.screenshot(path=screenshot_path)
                result['screenshot_path'] = screenshot_path
                result['detected'] = True
                
                logger.warning(f"📸 Screenshot saved: {screenshot_path}")
        
        except Exception as e:
            logger.debug(f"   ⚠️ Screenshot error: {e}")
        
        return result
    
    @staticmethod
    async def detect_submission_result(page, user: str, original_url: str = None) -> dict:
        """Detect result using multiple methods"""
        
        logger.debug(f"🎯 [{user}] Detecting submission result...")
        await asyncio.sleep(1.0)
        
        final_result = {
            'detected': False,
            'status': None,
            'text': '',
            'methods_tried': []
        }
        
        methods = [
            ResultDetector.detect_by_text,
            ResultDetector.detect_by_color,
            ResultDetector.detect_by_dom_change,
            ResultDetector.take_screenshot_for_debug,
        ]
        
        for method in methods:
            try:
                result = await method(page, user)
                final_result['methods_tried'].append(result)
                
                if result.get('detected') and result.get('status'):
                    final_result['detected'] = True
                    final_result['status'] = result['status']
                    final_result['text'] = result.get('text', '')
                    break
            
            except Exception as e:
                logger.debug(f"   ⚠️ Error with {method.__name__}: {e}")
        
        if not final_result['status']:
            logger.warning(f"⚠️ [{user}] Could not clearly detect result, assuming SUCCESS")
            final_result['status'] = 'SUCCESS'
        
        return final_result

def get_result_detector():
    """Get result detector instance"""
    return ResultDetector()
