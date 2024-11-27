import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("ALLaM-Chat")
    logger.setLevel(logging.DEBUG)

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    rotating_handler = RotatingFileHandler(
        log_dir / f"allam_chat_{current_time}.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=50,
        encoding="utf-8",
    )
    rotating_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    rotating_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    logger.addHandler(rotating_handler)
    logger.addHandler(console_handler)

    return logger
