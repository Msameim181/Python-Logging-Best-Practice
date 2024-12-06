import logging
import logging.handlers
import queue
import socket

from .logging_settings import (
    ApplicationLevelFilter,
    ColoredFormatter,
    IgnoreNANTraceFormatter,
    LoggingSettings,
    SysLogFormatter,
)
from .tracer import RequestIdFilter


class LoggingConfig:
    def __init__(self, settings: LoggingSettings):
        self.settings = settings
        self._configured = False
        if self.settings.enable_tracing:
            self.request_id_filter = RequestIdFilter()
        if self.settings.application_level:
            self.application_level_filter = ApplicationLevelFilter(
                self.settings.application_level
            )

    def configure(self):
        if self._configured:
            return

        # Set root logger level
        logging.getLogger().setLevel(self.settings.log_level)

    def get_logger(self, name: str) -> logging.Logger:
        if not self._configured:
            self.configure()

        logger = logging.getLogger(name)
        logger.propagate = False  # Prevent double logging

        # Add handlers if they don't exist
        if not logger.handlers:
            self._setup_handlers(logger)

        return logger

    def _set_logger_settings(
        self,
        handler: logging.handlers,
        formatter: logging.Formatter,
        logger: logging.Logger,
    ):
        handler.setFormatter(formatter)
        if self.settings.enable_tracing:
            handler.addFilter(self.request_id_filter)
        if self.settings.application_level:
            handler.addFilter(self.application_level_filter)
        logger.addHandler(handler)

    def _setup_console_handler(
        self, logger: logging.Logger, formatter: logging.Formatter
    ):
        if self.settings.enable_console_logging:
            console_handler = logging.StreamHandler()
            self._set_logger_settings(console_handler, formatter, logger)
            return console_handler
        return

    def _setup_file_handler(self, logger: logging.Logger, formatter: logging.Formatter):
        if self.settings.enable_file_logging:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=str(self.settings.file_path),
                maxBytes=self.settings.max_bytes,
                backupCount=self.settings.backup_count,
                encoding="utf-8",
            )
            self._set_logger_settings(file_handler, formatter, logger)
            return file_handler
        return

    def _setup_syslog_handler(
        self, logger: logging.Logger, formatter: logging.Formatter
    ):
        if not self.settings.syslog_host or not self.settings.syslog_port:
            return

        try:
            syslog_formatter = SysLogFormatter(
                fmt=self.settings.log_format,
                datefmt=self.settings.date_format,
                style=self.settings.style,
            )

            # Create handler with socket handling
            syslog_handler = logging.handlers.SysLogHandler(
                address=(self.settings.syslog_host, self.settings.syslog_port),
                facility=logging.handlers.SysLogHandler.LOG_USER,
                socktype=socket.SOCK_DGRAM,
            )

            # Add error handler
            syslog_handler.handleError = lambda *args, **kwargs: None

            self._set_logger_settings(syslog_handler, syslog_formatter, logger)

            return syslog_handler

        except (socket.error, OSError) as e:
            # Fallback to console logging if syslog fails
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)
            logger.warning(f"Failed to setup syslog handler: {str(e)}")
            print(f"Failed to setup syslog handler: {str(e)}")

    def _setup_handlers(self, logger: logging.Logger):
        formatter = ColoredFormatter(
            fmt=self.settings.log_format,
            datefmt=self.settings.date_format,
            style=self.settings.style,
        )
        if self.settings.enable_tracing and self.settings.ignore_nan_trace:
            formatter = IgnoreNANTraceFormatter(
                fmt=self.settings.log_format,
                datefmt=self.settings.date_format,
                style=self.settings.style,
            )

        # Queue handler
        log_queue = queue.Queue()

        # Console handler
        console_handler = self._setup_console_handler(logger, formatter)

        # File handler with rotation
        file_handler = self._setup_file_handler(logger, formatter)

        # Setup syslog with error handling
        syslog_handler = self._setup_syslog_handler(logger, formatter)

        # Queue listener
        handlers = [console_handler, file_handler, syslog_handler]
        queue_listener = logging.handlers.QueueListener(
            log_queue, *handlers, respect_handler_level=True
        )
        queue_listener.start()
