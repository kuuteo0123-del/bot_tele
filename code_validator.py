"""ุ
🔍 CODE VALIDATOR - Kiểm tra code hợp lệ
"""

import re
from logger_setup import logger
from config import Config

class CodeValidator:
    """Validate gift codes"""
    
    @staticmethod
    def validate_code(code: str, target_url: str) -> dict:
        """Kiểm tra code hợp lệ"""
        
        # Kiểm tra độ dài
        if len(code) < Config.CODE_MIN_LENGTH or len(code) > Config.CODE_MAX_LENGTH:
            return {'valid': False, 'reason': 'Invalid length'}
        
        # Kiểm tra ký tự
        if not re.match(r'^[a-zA-Z0-9]+$', code):
            return {'valid': False, 'reason': 'Invalid characters'}
        
        # Kiểm tra blacklist
        blacklist = [b.upper() for b in Config.CODE_BLACKLIST]
        if any(b in code.upper() for b in blacklist):
            return {'valid': False, 'reason': 'Blacklisted'}
        
        return {'valid': True, 'reason': 'OK'}
