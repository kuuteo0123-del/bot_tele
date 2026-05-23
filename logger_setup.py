"""ุ
📝 LOGGER SETUP - Cấu hình logging
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import Config

# Tạo thư mục logs
Path(Config.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

# Setup logger
logger = logging.getLogger('bot_tele')
logger.setLevel(Config.LOG_LEVEL)

# Format
formatter = logging.Formatter(Config.LOG_FORMAT)

# File handler
file_handler = RotatingFileHandler(
    Config.LOG_FILE,
    maxBytes=Config.MAX_LOG_SIZE,
    backupCount=Config.BACKUP_COUNT
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
if Config.CONSOLE_LOG:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
