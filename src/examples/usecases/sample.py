import asyncio
import logging

from chromatrace import LoggingConfig, get_trace_id


class AnotherSample:
    def __init__(self, logging_config: LoggingConfig):
        self.logger = logging_config.get_logger(self.__class__.__name__)
        self.background_task = set()
        self.logger.setLevel(logging.DEBUG)

    def do_something(self):
        self.logger.debug("Check something")
        self.logger.info("Doing something")
        self.logger.warning("Doing something")
        self.logger.error("Something went wrong")

    async def consume(self):
        trace_id = get_trace_id()
        self.logger.info(f"Consuming on {trace_id}")
        self.background_task.add(asyncio.create_task(self.run()))

    async def run(self):
        self.logger.info("Starting background task")
        self.logger.info("Background task started")
        await asyncio.sleep(5)
        self.logger.info("Stopping background task")
        self.logger.info("Background task stopped")

    async def send_http_request_with_trace_id(self):
        self.logger.info("Sending HTTP request with trace id")
        trace_id = get_trace_id()
        self.background_task.add(asyncio.create_task(self.send_http_request(trace_id)))

    async def send_http_request(self, trace_id: str):
        self.logger.info(f"Sending HTTP request with trace id: {trace_id}")
        await asyncio.sleep(5)
        self.logger.info("HTTP request completed")
