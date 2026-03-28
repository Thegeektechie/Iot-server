import logging
import os
from logging.handlers import RotatingFileHandler


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # === FORMATTER ===
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s | %(message)s"
    )

    # === CONSOLE HANDLER ===
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # === FILE HANDLER (ROTATING) ===
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "server.log"),
        maxBytes=5 * 1024 * 1024,   # 5 MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)

    # === ERROR FILE HANDLER ===
    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "error.log"),
        maxBytes=2 * 1024 * 1024,
        backupCount=2
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # === ADD HANDLERS ===
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger