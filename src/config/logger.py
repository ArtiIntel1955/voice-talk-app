"""Logging Configuration"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from .settings import get_settings


class LoggerManager:
    """Manager for application logging configuration"""

    _initialized = False
    _logger: Optional[logging.Logger] = None

    @classmethod
    def initialize(cls) -> logging.Logger:
        """Initialize logging configuration"""
        if cls._initialized:
            return cls._logger

        settings = get_settings()
        log_settings = settings.logging

        # Create log directory if it doesn't exist
        log_file = Path(log_settings.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create logger
        logger = logging.getLogger("voice_talk_app")
        logger.setLevel(log_settings.level)

        # Remove existing handlers
        logger.handlers = []

        # Create formatters
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_settings.level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=log_settings.max_size_mb * 1024 * 1024,
            backupCount=log_settings.backup_count
        )
        file_handler.setLevel(log_settings.level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        cls._initialized = True
        cls._logger = logger

        logger.info(f"Logging initialized: {log_file}")
        logger.info(f"Log level: {log_settings.level}")

        return logger

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get logger instance, initializing if necessary"""
        if not cls._initialized:
            return cls.initialize()
        return cls._logger


def get_logger(name: str = "voice_talk_app") -> logging.Logger:
    """Get logger instance for a specific module"""
    manager = LoggerManager.get_logger()
    return logging.getLogger(name)


def setup_logging():
    """Setup logging for the application"""
    LoggerManager.initialize()
