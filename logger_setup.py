import logging
import logging.handlers
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ColoredFormatter(logging.Formatter):
    """Formatter với màu sắc cho console"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logger():
    """Cấu hình logging hệ thống"""
    
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger("bot_logger")
    logger.setLevel(logging.INFO)
    
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/bot_activity.log",
        maxBytes=10485760,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = ColoredFormatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()