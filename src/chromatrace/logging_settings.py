import logging
from copy import copy
from pathlib import Path
from typing import Literal, Optional

import click
from pydantic import BaseModel


class LoggingSettings(BaseModel):
    application_level: str = ""
    log_level: str = "INFO"
    log_format: str = "(%(asctime)s)-[%(levelname)s]-[%(name)s]-FILENAME:%(filename)s-FUNC:%(funcName)s-THREAD:%(threadName)s-LINE:%(lineno)d :: %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    style: str = "%"
    file_path: Path = Path("./logs/app.log")
    max_bytes: int = 500 * 1024 * 1024  # 500MB
    backup_count: int = 3  # 3 days retention
    syslog_host: Optional[str] = None
    syslog_port: Optional[int] = None
    enable_console_logging: bool = True
    enable_file_logging: bool = False
    enable_tracing: bool = True
    ignore_nan_trace: bool = True
    use_console_colored_formatter: bool = True
    use_syslog_colored_formatter: bool = False
    use_file_colored_formatter: bool = False
    show_process_id: bool = False

    def __init__(self, **data):
        super().__init__(**data)
        if self.enable_file_logging:
            if isinstance(self.file_path, str):
                self.file_path = Path(self.file_path)
            if isinstance(self.file_path, Path):
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if self.application_level:
            self.log_format = "[%(application_level)s]-" + self.log_format
        if self.enable_tracing:
            self.log_format = "[%(trace_id)s]-" + self.log_format
        if self.show_process_id:
            self.log_format = self.log_format.replace(
                "(%(asctime)s)-", "(%(asctime)s)-[%(process)s]-"
            )




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
        self._trace_id_color_format = "\033[96m{}\033[0m"  # Cyan
        self.splitter = "\n"  # To add a newline after each log message

    def format(self, record):
        record.levelname = self._level_color_format.get(record.levelno, "").format(
            record.levelname
        )
        record.msg = self._message_color_format.format(record.msg)
        record.name = self._name_color_format.format(record.name)
        record.trace_id = self._trace_id_color_format.format(
            getattr(record, "trace_id", "NAN")
        )
        return super(ColoredFormatter, self).format(record) + self.splitter


class PlainFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)
        self.splitter = "\n"  # To add a newline after each log message

    def format(self, record):
        # clear all color codes and msg bold
        record.msg = record.msg.replace("\033[1m", "").replace("\033[0m", "")
        record.levelname = (
            record.levelname.replace("\033[94m", "")
            .replace("\033[92m", "")
            .replace("\033[93m", "")
            .replace("\033[91m", "")
            .replace("\033[95m", "")
            .replace("\033[0m", "")
        )
        record.name = record.name.replace("\033[90m", "").replace("\033[0m", "")
        return super(PlainFormatter, self).format(record) + self.splitter


class IgnoreNANTraceFormatter(ColoredFormatter):
    def format(self, record):
        try:
            message = super().format(record)
            message = message.replace("[\033[96mNAN\033[0m]-", "")
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


class PlainSysLogFormatter(PlainFormatter):
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
