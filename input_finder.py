"""
🔍 SMART INPUT FINDER - Advanced input detection with 10+ strategies (FIX #3)
"""

import asyncio
from logger_setup import logger

class SmartInputFinder:
    """Find input fields using multiple strategies"""
    
    USERNAME_SELECTORS = [
        ("input[placeholder*='tài' i]", "Vietnamese: tài khoản"),
        ("input[placeholder*='username' i]", "English: username"),
        ("input[placeholder*='account' i]", "English: account"),
        ("input[placeholder*='user' i]", "English: user"),
        ("input[placeholder*='đăng nhập' i]", "Vietnamese: login"),
        ("input[name='username']", "Name: username"),
        ("input[name='user']", "Name: user"),
        ("input#username", "ID: username"),
        ("input#user", "ID: user"),
        ("input[type='text']:not([type='hidden']):nth-of-type(1)", "First text input"),
    ]
    
    CODE_SELECTORS = [
        ("input[placeholder*='code' i]", "Placeholder: code"),
        ("input[placeholder*='mã' i]", "Vietnamese: mã"),
        ("input[placeholder*='gift' i]", "Placeholder: gift"),
        ("input[placeholder*='giftcode' i]", "Placeholder: giftcode"),
        ("input[placeholder*='redeem' i]", "Placeholder: redeem"),
        ("input[placeholder*='promo' i]", "Placeholder: promo"),
        ("input[name='code']", "Name: code"),
        ("input[name='giftcode']", "Name: giftcode"),
        ("input#code", "ID: code"),
        ("input#giftcode", "ID: giftcode"),
        ("input[type='text']:not([type='hidden']):nth-of-type(2)", "Second text input"),
    ]
    
    @staticmethod
    async def find_input_by_selector(page, selector: str, description: str):
        """Find single input by selector"""
        try:
            elem = await page.query_selector(selector)
            
            if elem:
                try:
                    if await elem.is_visible():
                        logger.debug(f"   ✅ Found via: {description}")
                        return elem
                    else:
                        logger.debug(f"   ⚠️ Found but hidden: {description}")
                except:
                    pass
        
        except Exception as e:
            logger.debug(f"   ❌ Error checking {description}: {e}")
        
        return None
    
    @staticmethod
    async def find_username_input(page, user: str):
        """Find username input field"""
        logger.debug(f"🔍 [{user}] Searching for username input...")
        
        for selector, description in SmartInputFinder.USERNAME_SELECTORS:
            result = await SmartInputFinder.find_input_by_selector(page, selector, description)
            if result:
                return result
        
        logger.warning(f"⚠️ [{user}] Could not find username input")
        return None
    
    @staticmethod
    async def find_code_input(page, user: str, skip_element=None):
        """Find code input field"""
        logger.debug(f"🔍 [{user}] Searching for code input...")
        
        for selector, description in SmartInputFinder.CODE_SELECTORS:
            result = await SmartInputFinder.find_input_by_selector(page, selector, description)
            
            if result and result != skip_element:
                return result
        
        logger.warning(f"⚠️ [{user}] Could not find code input")
        return None
    
    @staticmethod
    async def find_all_visible_inputs(page, user: str):
        """Get all visible input fields as fallback"""
        try:
            inputs = await page.query_selector_all(
                "input:not([type='hidden']):not([type='checkbox']):not([type='radio'])"
            )
            
            visible_inputs = []
            for inp in inputs:
                try:
                    if await inp.is_visible():
                        visible_inputs.append(inp)
                except:
                    pass
            
            logger.debug(f"   Found {len(visible_inputs)} visible inputs")
            return visible_inputs
        
        except Exception as e:
            logger.error(f"❌ [{user}] Error getting visible inputs: {e}")
            return []
    
    @staticmethod
    async def find_input_fields(page, user: str):
        """Find both username and code inputs with smart fallback"""
        
        try:
            logger.info(f"🔎 [{user}] Detecting input fields...")
            
            username_input = await SmartInputFinder.find_username_input(page, user)
            code_input = await SmartInputFinder.find_code_input(page, user, username_input)
            
            if not username_input or not code_input:
                logger.debug(f"   📍 Fallback: Using visible inputs")
                visible_inputs = await SmartInputFinder.find_all_visible_inputs(page, user)
                
                if len(visible_inputs) >= 2:
                    if not username_input:
                        username_input = visible_inputs[0]
                        logger.debug(f"   ✅ Using visible input #1 for username")
                    
                    if not code_input and len(visible_inputs) > 1:
                        code_input = visible_inputs[1]
                        logger.debug(f"   ✅ Using visible input #2 for code")
            
            if not username_input or not code_input:
                logger.error(f"❌ [{user}] Could not find all required inputs!")
                logger.error(f"   Username: {'✅' if username_input else '❌'}")
                logger.error(f"   Code: {'✅' if code_input else '❌'}")
                return None, None
            
            logger.info(f"✅ [{user}] Input detection successful")
            return username_input, code_input
        
        except Exception as e:
            logger.error(f"❌ [{user}] Error detecting inputs: {e}")
            return None, None

def get_input_finder():
    """Get input finder instance"""
    return SmartInputFinder()
