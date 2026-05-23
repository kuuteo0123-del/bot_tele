"""
📝 LOGGER SETUP - Enhanced logging with better formatting (FIX #10)
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/bot_activity.log')
MAX_LOG_SIZE = int(os.getenv('MAX_LOG_SIZE', 10485760))
BACKUP_COUNT = int(os.getenv('BACKUP_COUNT', 5))

def setup_logger():
    """Setup enhanced logger with multiple handlers"""
    
    logger = logging.getLogger('bot_tele')
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    logger.handlers = []
    
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[36m',
            'INFO': '\033[32m',
            'WARNING': '\033[33m',
            'ERROR': '\033[31m',
            'CRITICAL': '\033[35m',
        }
        RESET = '\033[0m'
        
        def format(self, record):
            log_color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{log_color}{record.levelname}{self.RESET}"
            return super().format(record)
    
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT
        )
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"⚠️ Could not setup file handler: {e}")
    
    try:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    except Exception as e:
        print(f"⚠️ Could not setup console handler: {e}")
    
    return logger

logger = setup_logger()

def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)
