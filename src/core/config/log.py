import logging
from pathlib import Path
from typing import Any, Literal

from pydantic.v1 import BaseSettings
from uvicorn.logging import AccessFormatter, DefaultFormatter


class LoggingSettings(BaseSettings):
    LOGGING_LEVEL_CONSOLE: int | str = logging.INFO
    LOGGING_LEVEL_FILE: int | str = logging.WARNING

    LOG_PATH: Path = Path("/") / "mnt" / "efs" / "logs" / "file-receiver"

    LOG_FILE_MAX_SIZE: int = 10
    LOG_FILE_BACKUP_COUNT: int = 5

    DEFAULT_HANDLERS = Literal[
        "console",
        "access",
        "file_access",
        "file_errors",
    ]

    DEFAULT_FORMATTER = DefaultFormatter(
        fmt="%(levelprefix)s %(message)s",
        use_colors=True,
    )

    @staticmethod
    def to_handlers(handlers: list[DEFAULT_HANDLERS] | None = None, propagate: bool = False, **kwargs: Any) -> dict:
        return {"handlers": handlers or [], "propagate": propagate, **kwargs}

    def set_default_formatter_to_loggers(self) -> None:
        for logger_name in logging.root.manager.loggerDict.keys():
            logger = logging.getLogger(logger_name)

            for handler in logger.handlers:
                handler.setFormatter(self.DEFAULT_FORMATTER)

    def file_handler(self, file_name: str, level: int | str | None = None) -> dict:
        return {
            "formatter": "file",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": self.LOG_PATH / file_name,
            "backupCount": self.LOG_FILE_BACKUP_COUNT,
            "maxBytes": self.LOG_FILE_MAX_SIZE * 1024**2,
            "level": level or self.LOGGING_LEVEL_FILE,
        }

    def configure(self) -> dict:
        self.LOG_PATH.mkdir(parents=True, exist_ok=True)
        self.set_default_formatter_to_loggers()
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": DefaultFormatter,
                    "fmt": "%(levelprefix)s %(message)s",
                    "use_colors": True,
                },
                "file": {
                    "()": DefaultFormatter,
                    "fmt": "%(asctime)s %(levelprefix)s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "access": {
                    "()": AccessFormatter,
                    "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                    "use_colors": True,
                },
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "level": self.LOGGING_LEVEL_CONSOLE,
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "level": self.LOGGING_LEVEL_CONSOLE,
                },
                "file_access": self.file_handler("access.log", logging.INFO),
                "file_errors": self.file_handler("errors.log"),
            },
            "loggers": {
                "uvicorn": self.to_handlers(["console"]),
                "uvicorn.access": self.to_handlers(["access", "file_access"]),
                "uvicorn.error": self.to_handlers(["console", "file_errors"]),
            },
        }


logging_settings = LoggingSettings()
LOGGING = logging_settings.configure()
