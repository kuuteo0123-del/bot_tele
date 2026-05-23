"""
📋 CODE VALIDATOR (v3.6.2 - FIXED)
Xác thực và phân tích độ tin cậy của code - Đồng bộ với config
"""

import re
import math
from config import Config
from logger_setup import logger

class CodeValidator:
    """Xác thực và phân tích độ tin cậy của code"""
    
    WEB_PATTERNS = {
        "https://new88b.today/giftcode": {
            "name": "NEW88",
            "min_length": Config.CODE_MIN_LENGTH,
            "max_length": Config.CODE_MAX_LENGTH,
            "pattern": rf"^[a-zA-Z0-9]{{{Config.CODE_MIN_LENGTH},{Config.CODE_MAX_LENGTH}}}$",
            "common_prefixes": ["NEW", "N88", "CODE"],
            "confidence_threshold": 0.7,
        },
        "https://mm88code.com": {
            "name": "MM88",
            "min_length": Config.CODE_MIN_LENGTH,
            "max_length": Config.CODE_MAX_LENGTH,
            "pattern": rf"^[a-zA-Z0-9]{{{Config.CODE_MIN_LENGTH},{Config.CODE_MAX_LENGTH}}}$",
            "common_prefixes": ["MM", "M88", "CODE"],
            "confidence_threshold": 0.7,
        },
        "https://llwincode.com/": {
            "name": "LLwin",
            "min_length": Config.CODE_MIN_LENGTH,
            "max_length": Config.CODE_MAX_LENGTH,
            "pattern": rf"^[a-zA-Z0-9]{{{Config.CODE_MIN_LENGTH},{Config.CODE_MAX_LENGTH}}}$",
            "common_prefixes": ["LL", "LLW", "WIN"],
            "confidence_threshold": 0.7,
        },
    }
    
    FAKE_CODE_PATTERNS = [
        r"^(TEST|DEMO|EXAMPLE|FAKE|XXX|SAMPLE)",
        r"^(ABC|DEF|GHI|JKL|MNO|PQR|STU|VWX|YZ)",
        r"^123|^456|^789|^000|^111|^222|^333|^444|^555|^666|^777|^888|^999",
        r"^AAAA|^BBBB|^CCCC|^DDDD|^EEEE|^FFFF|^GGGG|^HHHH|^IIII|^JJJJ",
    ]
    
    HISTORY_FILE = "code_history.txt"
    
    @staticmethod
    def calculate_entropy(code):
        """Calculate Shannon entropy of code"""
        if not code:
            return 0
        char_freq = {}
        for char in code:
            char_freq[char] = char_freq.get(char, 0) + 1
        entropy = 0
        code_len = len(code)
        for freq in char_freq.values():
            p = freq / code_len
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    @staticmethod
    def is_sequential_code(code):
        """Check if code is sequential (suspicious)"""
        if re.match(r"^[a-zA-Z]{4,}$|^[0-9]{4,}$", code):
            char_list = list(code)
            if all(c == char_list[0] for c in char_list):
                return True
        if re.match(r"^[a-zA-Z0-9]{2,}$", code):
            pattern = code[:2]
            if all(code[i:i+2] == pattern for i in range(0, len(code), 2)):
                return True
        return False
    
    @staticmethod
    def is_likely_fake(code):
        """Check if code is likely fake"""
        code_upper = code.upper()
        for fake_pattern in CodeValidator.FAKE_CODE_PATTERNS:
            if re.match(fake_pattern, code_upper):
                return True
        if CodeValidator.is_sequential_code(code):
            return True
        entropy = CodeValidator.calculate_entropy(code)
        if entropy < 1.5:  # FIXED: Lowered from 2.0 to be less strict
            return True
        return False
    
    @classmethod
    def validate_code(cls, code, target_url=""):
        """Validate code with improved entropy handling"""
        result = {
            'valid': False,
            'confidence': 0.0,
            'reason': '',
            'is_fake': False,
            'entropy': 0.0,
            'recommendation': 'SKIP'
        }
        
        # ✅ Dùng độ dài từ config
        min_len = Config.CODE_MIN_LENGTH
        max_len = Config.CODE_MAX_LENGTH
        if len(code) < min_len or len(code) > max_len:
            result['reason'] = f"❌ Độ dài không hợp lệ: {len(code)} (yêu cầu {min_len}-{max_len})"
            return result
            
        if not re.match(r"^[a-zA-Z0-9]+$", code):
            result['reason'] = "❌ Chứa ký tự không hợp lệ"
            return result
            
        entropy = cls.calculate_entropy(code)
        result['entropy'] = round(entropy, 2)
        
        if cls.is_likely_fake(code):
            result['is_fake'] = True
            result['confidence'] = 0.1
            result['reason'] = "🚫 Code có dấu hiệu giả mạo"
            result['recommendation'] = 'SKIP'
            return result
        
        if not result['is_fake']:
            # FIXED: More lenient entropy thresholds
            if entropy >= 4.0:
                result['confidence'] = 0.95
                result['valid'] = True
                result['reason'] = "✅ Code hợp lệ, entropy cao (random)"
                result['recommendation'] = 'SUBMIT'
            elif entropy >= 3.0:
                result['confidence'] = 0.85
                result['valid'] = True
                result['reason'] = "✅ Code hợp lệ, entropy trung bình"
                result['recommendation'] = 'SUBMIT'
            elif entropy >= 2.0:
                result['confidence'] = 0.70
                result['valid'] = True
                result['reason'] = "✅ Code hợp lệ (entropy thấp nhưng được phép)"
                result['recommendation'] = 'SUBMIT'
            else:
                result['confidence'] = 0.50
                result['valid'] = True
                result['reason'] = "⚠️ Code có entropy rất thấp nhưng không phải fake"
                result['recommendation'] = 'SUBMIT'
        return result
    
    @staticmethod
    def get_confidence_emoji(confidence):
        if confidence >= 0.90: return "🟢"
        elif confidence >= 0.70: return "🟡"
        elif confidence >= 0.50: return "🟠"
        elif confidence >= 0.30: return "🔴"
        else: return "⚫"
    
    @staticmethod
    def log_validation_result(code, validation_result):
        emoji = CodeValidator.get_confidence_emoji(validation_result['confidence'])
        logger.info(f"\n{'='*60}")
        logger.info(f"📋 PHÂN TÍCH CODE: {code}")
        logger.info(f"{emoji} Tin cậy: {validation_result['confidence']:.0%}")
        logger.info(f"🔍 Entropy: {validation_result['entropy']:.2f}")
        logger.info(f"💬 {validation_result['reason']}")
        logger.info(f"🎯 Khuyến nghị: {validation_result['recommendation']}")
        logger.info(f"{'='*60}\n")
