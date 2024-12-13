import http
import logging
import sys
from copy import copy
from typing import Literal

import click

TRACE_LOG_LEVEL = 5


class BasicFormatter(logging.Formatter):
    """
    A custom log formatter class that:

    * Outputs the LOG_LEVEL with an appropriate color.
    * If a log call includes an `extras={"color_message": ...}` it will be used
      for formatting the output, instead of the plain text message.
    """

    _level_name_colors = {
        TRACE_LOG_LEVEL: lambda level_name: click.style(
            str(level_name), fg="bright_blue"
        ),
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="blue"),
        logging.INFO: lambda level_name: click.style(
            str(level_name), fg="green", blink=True
        ),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(str(level_name), fg="magenta"),
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = True,
    ):
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        def default(level_name: str) -> str:
            return str(level_name)  # pragma: no cover

        func = self._level_name_colors.get(level_no, default)
        return func(level_name)

    def should_use_colors(self) -> bool:
        return True  # pragma: no cover

    def get_colored_process_id(self, process_id: int) -> str:
        return click.style(process_id, fg="black")

    def get_process_id_line(self, process_id: int) -> str:
        return f"PID:{process_id}"

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)
        process = self.get_process_id_line(record_copy.process)
        levelname = record_copy.levelname
        if self.use_colors:
            process = self.get_colored_process_id(process)
            levelname = self.color_level_name(levelname, record_copy.levelno)
            if "color_message" in record_copy.__dict__:
                record_copy.msg = record_copy.__dict__["color_message"]
                record_copy.__dict__["message"] = record_copy.getMessage()
        record_copy.__dict__["levelname"] = levelname
        record_copy.__dict__["process"] = process
        return super().formatMessage(record_copy)


class DefaultFormatter(BasicFormatter):
    def should_use_colors(self) -> bool:
        return sys.stderr.isatty()  # pragma: no cover


class AccessFormatter(BasicFormatter):
    status_code_colors = {
        1: lambda code: click.style(str(code), fg="bright_white"),
        2: lambda code: click.style(str(code), fg="green"),
        3: lambda code: click.style(str(code), fg="yellow"),
        4: lambda code: click.style(str(code), fg="red"),
        5: lambda code: click.style(str(code), fg="bright_red"),
    }
    method_colors = {
        "GET": lambda m: click.style(m, fg="green"),
        "POST": lambda m: click.style(m, fg="cyan"),
        "PUT": lambda m: click.style(m, fg="blue"),
        "DELETE": lambda m: click.style(m, fg="red"),
        "PATCH": lambda m: click.style(m, fg="magenta"),
        "HEAD": lambda m: click.style(m, fg="yellow"),
        "OPTIONS": lambda m: click.style(m, fg="white"),
        "TRACE": lambda m: click.style(m, fg="bright_black"),
    }

    def get_status_code(self, status_code: int) -> str:
        try:
            status_phrase = http.HTTPStatus(status_code).phrase
        except ValueError:
            status_phrase = ""
        status_and_phrase = f"{status_code} {status_phrase}"
        if self.use_colors:

            def default(code: int) -> str:
                return status_and_phrase

            func = self.status_code_colors.get(status_code // 100, default)
            return func(status_and_phrase)
        return status_and_phrase

    def get_colored_method(self, method: str) -> str:
        def default(method: str) -> str:
            return click.style(method, fg="white")

        func = self.method_colors.get(method.upper(), default)
        return func(method)

    def get_colored_path(self, path: str) -> str:
        return click.style(path, fg="bright_black")

    def get_colored_client_address(self, client_address: str) -> str:
        return click.style(client_address, fg="bright_black")

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)
        (
            client_addr,
            method,
            full_path,
            http_version,
            status_code,
        ) = record_copy.args
        status_detail = self.get_status_code(int(status_code))
        if self.use_colors:
            method = self.get_colored_method(method)
            full_path = self.get_colored_path(full_path)
            client_addr = self.get_colored_client_address(client_addr)
        request_detail = f"{method} {full_path} HTTP/{http_version}"
        record_copy.__dict__.update(
            {
                "client_address": client_addr,
                "request_detail": request_detail,
                "status_detail": status_detail,
            }
        )
        return super().formatMessage(record_copy)
