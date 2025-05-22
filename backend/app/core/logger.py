
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(
    name: str = "app",
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_file_path: str = "logs/app.log",
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 3
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid adding multiple handlers to the same logger
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    if log_to_file:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        fh = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
