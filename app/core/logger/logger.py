import logging
import logging.handlers
from datetime import datetime
import sys
import os
from pathlib import Path


class Logger:
    """Centralized logging configuration for the crawler engine."""

    _loggers = {}
    _configured = False

    @classmethod
    def configure(cls, log_level: str = "INFO", log_dir: str = "logs"):
        """Configure logging for the entire application."""
        if cls._configured:
            return

        # Create logs directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Define log format
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))

        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler (rotating file)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            filename=log_path / "error.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str = __name__) -> logging.Logger:
        """Get or create a logger for a specific module."""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        return cls._loggers[name]


# Convenience functions
def get_logger(name: str = __name__) -> logging.Logger:
    """Get a logger instance."""
    Logger.configure()
    return Logger.get_logger(name)


def configure_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """Configure logging at application startup."""
    Logger.configure(log_level=log_level, log_dir=log_dir)


# Use it
# logger.info("Creating intent job")
# logger.warning("Config not found")
# logger.error("Failed to process URL")
# logger.debug("Detailed debug info")
