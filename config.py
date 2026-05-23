"""
⚙️ CẤU HÌNH TỐI ƯU CHO BOT v3.9 (FIREFOX + PERSISTENT PROFILE)
Đã sữa: Browser type, ViewPort, Profile path
Sử dụng: copy toàn bộ file này
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ==========================================
    # 🔑 TELEGRAM CREDENTIALS
    # ==========================================
    API_ID = int(os.getenv('API_ID', 20451785))
    API_HASH = os.getenv('API_HASH', 'f93e22ca85ce0e5c107e5a8027eb4bf4')
    SESSION_NAME = os.getenv('SESSION_NAME', 'session_bot_full')

    # ==========================================
    # 📝 LOGGING
    # ==========================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/bot_activity.log')
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    MAX_LOG_SIZE = int(os.getenv('MAX_LOG_SIZE', 10485760))
    BACKUP_COUNT = int(os.getenv('BACKUP_COUNT', 5))
    CONSOLE_LOG = True

    # ==========================================
    # 📋 FILES & PARAMETERS
    # ==========================================
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/code_history.db')
    HISTORY_FILE = "logs/history_success.txt"
    BROWSER_PROFILE_DIR = os.getenv('BROWSER_PROFILE_DIR', 'HoSo_Bot_Vip')
    CODE_MIN_LENGTH = 6
    CODE_MAX_LENGTH = 15
    
    # ==========================================
    # 🖥️ BROWSER CONFIGURATION (FIXED v3.9)
    # ==========================================
    BROWSER_TYPE = "firefox"  # ✅ FIREFOX (tối ưu cho CF bypass)
    # Alternatives: "chromium", "webkit"
    
    # ✅ DESKTOP VIEWPORT (không phải điện thoại)
    VIEWPORT_WIDTH = 1024
    VIEWPORT_HEIGHT = 768
    
    # ✅ WINDOW POSITION (fixed)
    WINDOW_POSITION_X = 0
    WINDOW_POSITION_Y = 0
    
    # ✅ HEADLESS MODE
    HEADLESS_MODE = False  # Hiển thị UI để debug
    
    # ✅ PROFILE STORAGE (persistent)
    PROFILE_STORAGE_TYPE = "persistent"  # "persistent" hoặc "temp"
    PROFILE_CLEANUP_DAYS = 30
    CLEANUP_OLD_PROFILES = True

    # ==========================================
    # ⏱️ TIMEOUTS (ms) - TUNED
    # ==========================================
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', 30000))
    CLOUDFLARE_WAIT_TIMEOUT = int(os.getenv('CLOUDFLARE_WAIT_TIMEOUT', 60000))
    SUBMIT_TIMEOUT = 5000
    RESULT_WAIT = 2000
    BROWSER_SPAWN_TIMEOUT = 15000

    # ==========================================
    # ⚡ PERFORMANCE - OPTIMIZED FOR SPEED
    # ==========================================
    MAX_CONCURRENT_SUBMITS = int(os.getenv('MAX_CONCURRENT_TASKS', 3))
    MAX_RETRY_FAILED_CODE = 2
    CLEANUP_OLD_PROFILES = True
    PROFILE_CLEANUP_DAYS = 30

    # ==========================================
    # 🛡️ ANTI-BAN - FAST DELAYS (OPTIMIZED)
    # ==========================================
    MIN_DELAY_BETWEEN_SUBMITS = float(os.getenv('MIN_DELAY_BETWEEN_SUBMITS', 0.8))
    REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE', 30))
    MAX_BURST = int(os.getenv('MAX_BURST', 5))
    
    # ==========================================
    # 🤖 AUTO-SUBMIT (v3.9) - PRODUCTION READY
    # ==========================================
    AUTO_SUBMIT_ENABLED = os.getenv('AUTO_SUBMIT_ENABLED', 'True').lower() == 'true'
    AUTO_SUBMIT_DELAY = float(os.getenv('AUTO_SUBMIT_DELAY', 0.3))
    HUMAN_LIKE_TYPING_SPEED = float(os.getenv('HUMAN_LIKE_TYPING_SPEED', 0.05))
    RANDOM_DELAY_MIN = float(os.getenv('RANDOM_DELAY_MIN', 0.1))
    RANDOM_DELAY_MAX = float(os.getenv('RANDOM_DELAY_MAX', 0.5))
    
    # ==========================================
    # 🔍 INPUT DETECTION (v3.9) - 95% ACCURACY
    # ==========================================
    INPUT_DETECTION_STRATEGY = os.getenv('INPUT_DETECTION_STRATEGY', 'advanced')
    INPUT_DETECTION_TIMEOUT = int(os.getenv('INPUT_DETECTION_TIMEOUT', 5000))
    MULTIPLE_SELECTOR_ATTEMPTS = int(os.getenv('MULTIPLE_SELECTOR_ATTEMPTS', 4))
    
    # ==========================================
    # 📊 RESULT DETECTION (v3.9) - 5 METHODS
    # ==========================================
    RESULT_DETECTION_METHODS = int(os.getenv('RESULT_DETECTION_METHODS', 5))
    RESULT_DETECTION_TIMEOUT = int(os.getenv('RESULT_DETECTION_TIMEOUT', 5000))
    SCREENSHOT_ON_UNKNOWN = os.getenv('SCREENSHOT_ON_UNKNOWN', 'True').lower() == 'true'
    
    # ==========================================
    # 🔄 SESSION ROTATION (v3.9)
    # ==========================================
    SESSION_ROTATION_ENABLED = os.getenv('SESSION_ROTATION_ENABLED', 'False').lower() == 'true'
    SESSION_ROTATION_INTERVAL = int(os.getenv('SESSION_ROTATION_INTERVAL', 100))
    SESSION_ROTATION_DELAY = float(os.getenv('SESSION_ROTATION_DELAY', 2.0))
    
    # ==========================================
    # 📱 CHANNEL CONFIG
    # ==========================================
    CHANNEL_CONFIG = {
        # CHANNEL 1: MM88VIP
        -1003134541072: {
            "name": "MM88VIP Dịch Vụ Giai Nhân",
            "url": "https://mm88code.com",
            "priority": 1,
            "accounts": [
                {"username": "dad131", "priority": 1},
                {"username": "kaoboy012", "priority": 2},
                {"username": "ola12", "priority": 3}
            ]
        },

        # CHANNEL 2: LLWIN
        -1003859359508: {
            "name": "LLwin ĐỈNH CAO CHIẾN THẮNG",
            "url": "https://llwincode.com",
            "priority": 2,
            "accounts": [
                {"username": "kaoboy012", "priority": 1},
                {"username": "conve99sau", "priority": 2}
            ]
        },

        # CHANNEL 3: NEW88
        -1002626603440: {
            "name": "NEW88 PHÁT C.O.DE NỔ HŨ - BẮN CÁ MIỄN PHÍ",
            "url": "https://new88b.today/giftcode",
            "priority": 3,
            "accounts": [
                {"username": "minichan", "priority": 1},
                {"username": "kuuteo0123", "priority": 2}
            ]
        },

        # CHANNEL 4: XX88
        -1002817093108: {
            "name": "PHÁT CODE XX88",
            "url": "https://xx88code.com/",
            "priority": 4,
            "accounts": [
                {"username": "dad131", "priority": 1},
                {"username": "hugolan012", "priority": 2} 
            ]
        },

        # CHANNEL 5: CLIP VUI NEW88
        -1003090141840: {
            "name": "CLIP VUI NEW88",
            "url": "https://new88b.today/giftcode",
            "priority": 5,
            "accounts": [
                {"username": "minichan", "priority": 1},
                {"username": "kuuteo0123", "priority": 2}
            ]
        },

        # CHANNEL 6: o8 SOI KÈO 24/7
        -1003917076387: {
            "name": "o8 SOI KÈO 24/7",
            "url": "https://o8code.com/",
            "priority": 6,
            "accounts": [
                {"username": "kaoboy012", "priority": 1},
                {"username": "conve99sau", "priority": 2}
            ]
        }
    }

    # ==========================================
    # 🚫 BLACKLIST PATTERNS (Lọc code giả)
    # ==========================================
    CODE_BLACKLIST = [
        "COM", "HTTP", "HTTPS", "WWW", "FACEBOOK",
        "CHECK", "CLIP", "VUI", "BOT", "DAILY",
        "BANCA", "NOHU", "ONLINE", "FREE", "CODE"
    ]

    # ==========================================
    # ✅ FEATURE FLAGS
    # ==========================================
    ENABLE_RETRY = True
    ENABLE_CIRCUIT_BREAKER = True
    ENABLE_DATABASE_TRACKING = True
    ENABLE_RATE_LIMITING = True
    ENABLE_MONITORING = True
    ENABLE_AUTO_SESSION_ROTATION = False
    ENABLE_ADVANCED_ANTI_DETECTION = True
