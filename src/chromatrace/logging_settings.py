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


class BasicFormatter(logging.Formatter):
    TRACE_LOG_LEVEL = 5
    _level_color_format = {
        TRACE_LOG_LEVEL: lambda level_name: click.style(
            str(level_name), fg="bright_blue"
        ),
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="blue"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(str(level_name), fg="magenta"),
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        colored: bool | None = False,
        message_splitter: str | None = "\n",
        log_splitter: str | None = "\n",
        remove_nan_trace: bool | None = False,
    ):
        super().__init__(fmt, datefmt, style)
        self.log_splitter = (
            log_splitter or ""
        )  # To add a newline after each log message
        self.message_splitter = (
            message_splitter or ""
        )  # To add a newline before each message and the log details
        self.colored = colored
        self.remove_nan_trace = remove_nan_trace

    def _color_level_name(self, level_name: str, level_no: int) -> str:
        def default(level_name: str) -> str:
            return str(level_name)  # pragma: no cover

        func = self._level_color_format.get(level_no, default)
        return func(level_name)

    def _format_message(self, message: str) -> str:
        return click.style(message, bold=True)

    def _format_name(self, name: str) -> str:
        return click.style(name, fg="bright_black")

    def _format_trace_id(self, trace_id: str) -> str:
        return click.style(trace_id, fg="cyan")

    def _format_process_id(self, process_id: int) -> str:
        return click.style(process_id, fg="black")

    def format(self, record):
        record_copy = copy(record)
        record_copy.__dict__["process"] = f'PID:{getattr(record_copy, "process", 0)}'
        trace_id = getattr(record_copy, "trace_id", "NAN")
        if self.colored:
            record_copy.__dict__["levelname"] = self._color_level_name(
                level_name=record_copy.levelname, level_no=record_copy.levelno
            )
            record_copy.__dict__["msg"] = self._format_message(record_copy.msg)
            record_copy.__dict__["name"] = self._format_name(record_copy.name)
            record_copy.__dict__["process"] = self._format_process_id(
                record_copy.process
            )
            if not (trace_id == "NAN" and self.remove_nan_trace):
                record_copy.__dict__["trace_id"] = self._format_trace_id(trace_id)

        record_copy.__dict__["msg"] = (
            self.message_splitter + record_copy.__dict__["msg"]
        )
        message = super(BasicFormatter, self).format(record_copy) + self.log_splitter
        if self.remove_nan_trace:
            message = message.replace("[NAN]-", "")
        return message


class SysLogFormatter(BasicFormatter):
    def __init__(
        self,
        message_splitter: str | None = "",
        log_splitter: str | None = "",
        *args,
        **kwargs,
    ):
        super().__init__(
            message_splitter=message_splitter,
            log_splitter=log_splitter,
            *args,
            **kwargs,
        )


class ApplicationLevelFilter(logging.Filter):
    def __init__(self, application_level):
        super().__init__()
        self.application_level = application_level

    def filter(self, record):
        record.application_level = self.application_level
        return True
