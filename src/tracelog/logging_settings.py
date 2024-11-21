import logging
from pydantic import BaseModel
from pathlib import Path
from typing import Optional

class LoggingSettings(BaseModel):
    log_level: str = "INFO"
    log_format: str = "(%(asctime)s)-[%(levelname)s]-[%(name)s]-FILENAME:%(filename)s-FUNC:%(funcName)s-THREAD:%(threadName)s-LINE:%(lineno)d :: \n%(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    style: str = "%"
    file_path: Path = Path("./log/app.log")
    max_bytes: int = 500 * 1024 * 1024  # 500MB
    backup_count: int = 3  # 3 days retention
    syslog_host: Optional[str] = None
    syslog_port: Optional[int] = None


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)
        self._level_color_format = {
            logging.DEBUG: "\033[94m{}\033[0m",  # Blue
            logging.INFO: "\033[92m{}\033[0m",  # Green
            logging.WARNING: "\033[93m{}\033[0m",  # Yellow
            logging.ERROR: "\033[91m{}\033[0m",  # Red
            logging.CRITICAL: "\033[95m{}\033[0m",  # Magenta
        }
        self._message_color_format = "\033[1m{}\033[0m"  # Bold
        self._name_color_format = "\033[90m{}\033[0m"  # Gray
        self.splitter = "\n"  # To add a newline after each log message

    def format(self, record):
        record.levelname = self._level_color_format.get(record.levelno, "").format(
            record.levelname
        )
        record.msg = self._message_color_format.format(record.msg)
        record.name = self._name_color_format.format(record.name)
        return super(ColoredFormatter, self).format(record) + self.splitter

class IgnoreNANTraceFormatter(ColoredFormatter):
    def format(self, record):
        try:
            message = super().format(record)
            return message.replace("[NAN]-", "")
        except Exception:
            return record.getMessage()

class SysLogFormatter(ColoredFormatter):
    def format(self, record):
        try:
            message = super().format(record)
            return message.replace("\n", " | ")
        except Exception:
            return record.getMessage()


class ApplicationLevelFilter(logging.Filter):
    def __init__(self, application_level):
        super().__init__()
        self.application_level = application_level

    def filter(self, record):
        record.application_level = self.application_level
        return True



