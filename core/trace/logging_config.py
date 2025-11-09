"""
Logging configuration for the application.

This module defines custom formatters and logging configuration dictionaries
for use throughout the application.
"""

import logging


class CustomFormatter(logging.Formatter):
    """Custom formatter for logging that adds the logger name to the record."""

    def format(self, log: logging.LogRecord) -> str:
        """
        Format the log record by adding the logger name and delegating to the parent formatter.

        Args:
            log (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message.

        """
        log.logger_name = log.name
        return super().format(log)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {},
    "formatters": {
        "default_formatter": {
            "()": CustomFormatter,
            "format": "%(asctime)s - %(levelname)s - [%(name)s:%(filename)s:%(lineno)d] - User: %(user)s \n%(message)s",
            "defaults": {"user": "None"},
        }
    },
    "handlers": {
        "default_stream": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "default_formatter"},
        "eval_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default_formatter",
            "filename": "logs/app.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8",
        },
        "eval_error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default_formatter",
            "filename": "logs/error.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "ui": {"level": "INFO", "handlers": ["default_stream"]},
        "agentic_chatbot": {"level": "DEBUG", "handlers": ["default_stream"]},
        "eval": {"level": "INFO", "handlers": ["default_stream", "eval_file", "eval_error_file"]},
    },
}
