"""日志管理模块"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "japanese_learning", 
                level: str = "INFO") -> logging.Logger:
    """设置日志器"""

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 文件处理器
    log_file = Path("logs") / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    log_file.parent.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 默认日志器
logger = setup_logger()
