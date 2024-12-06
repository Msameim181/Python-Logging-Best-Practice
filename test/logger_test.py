import asyncio
import logging
import os
from io import StringIO

import pytest
from chromatrace import FastAPIRequestIdMiddleware as FastAPIMiddleware
from chromatrace import (
    LoggingConfig,
    LoggingSettings,
    RequestIdContext,
    SocketRequestIdMiddleware,
    trace_id_ctx,
    tracer,
)
from chromatrace.logging_settings import IgnoreNANTraceFormatter
from chromatrace.tracer import RequestIdFilter
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestLoggingConfiguration:
    @pytest.fixture(scope="class")
    def settings(self):
        return LoggingSettings(
            log_level="INFO",
            enable_console_logging=True,
            enable_file_logging=True,
            enable_tracing=True,
            application_level="TestLoggingConfiguration",
            file_path="test.log",
        )

    def test_basic_logging_setup(self, settings):
        config = LoggingConfig(settings)
        logger = config.get_logger("configuration")
        logger.setLevel(settings.log_level)
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO

    def test_file_logging(self, settings):
        config = LoggingConfig(settings)
        logger = config.get_logger("configuration")
        logger.info("Test message")
        assert os.path.exists(settings.file_path)

    def test_tracing_enabled(self, settings):
        config = LoggingConfig(settings)
        logger = config.get_logger("configuration")
        with RequestIdContext("test-id"):
            logger.info("Test message")
            assert trace_id_ctx.get() == "R-test-id"


class TestRequestIdMiddleware:
    @pytest.fixture
    def fastapi_app(self):
        app = FastAPI()
        app.add_middleware(FastAPIMiddleware)

        @app.get("/")
        async def root():
            return {"trace_id": trace_id_ctx.get()}

        return app

    def test_fastapi_middleware(self, fastapi_app):
        client = TestClient(fastapi_app)
        response = client.get("/", headers={"X-Request-ID": "test-id"})
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] is not None

    def test_socketio_middleware(self):
        async def test_app(scope, receive, send):
            assert trace_id_ctx.get() is not None

        app = SocketRequestIdMiddleware(test_app)
        scope = {"headers": [(b"x-trace-id", b"test-id")]}

        async def run_test():
            await app(scope, None, None)

        asyncio.run(run_test())


class TestTracerDecorator:
    @tracer
    async def async_function(self):
        return trace_id_ctx.get()

    @tracer
    def sync_function(self):
        return trace_id_ctx.get()

    def test_sync_tracer(self):
        result = self.sync_function()
        assert result.startswith("T-")

    @pytest.mark.asyncio
    async def test_async_tracer(self):
        result = await self.async_function()
        assert result.startswith("T-")


class TestFormatters:
    @pytest.fixture(scope="class")
    def settings(self):
        return LoggingSettings(
            application_level="TestFormatters",
            enable_console_logging=True,
            enable_tracing=True,
            ignore_nan_trace=True,
        )

    @pytest.fixture
    def stream(self):
        return StringIO()

    @pytest.fixture
    def logger(self, settings, stream):
        # Clear all existing loggers
        config = LoggingConfig(settings)
        logger = config.get_logger("formatter-test")

        # Add StreamHandler directly to logger
        handler = logging.StreamHandler(stream)
        handler.setFormatter(
            IgnoreNANTraceFormatter(
                fmt=settings.log_format,
                datefmt=settings.date_format,
                style=settings.style,
            )
        )
        logger.addHandler(handler)
        return logger

    def test_colored_output(self, logger, stream):
        with RequestIdContext("test-id"):
            logger.info("Test message")
            output = stream.getvalue()

        assert "\033[" in output  # ANSI color codes
        assert "Test message" in output
        assert "test-id" in output

    def test_ignore_nan_trace(self, logger, stream):
        logger.info("Test message with no trace...")
        assert "NAN" not in logger.handlers[0].format(
            logging.LogRecord("", 0, "", 0, "msg", (), None)
        )


class TestContextManagement:
    def test_nested_context(self):
        with RequestIdContext("outer"):
            assert trace_id_ctx.get() == "R-outer"
            with RequestIdContext("inner"):
                assert trace_id_ctx.get() == "R-inner"
            assert trace_id_ctx.get() == "R-outer"

    def test_request_id_filter(self):
        filter = RequestIdFilter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        filter.filter(record)
        assert hasattr(record, "trace_id")
