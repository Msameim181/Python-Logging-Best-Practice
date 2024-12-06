import asyncio
import sys

import injection  # noqa
from api_app import APIService
from dependency import container
from example_service import ExampleService
from sample import AnotherSample
from socket_app import SocketService
from src.chromatrace import LoggingConfig, LoggingSettings, tracer

sys.stdout.reconfigure(encoding="utf-8")


def api_app():
    return container[APIService].rest_application


def socket_app():
    return container[SocketService].socket_application


@tracer
def main():
    # Optional: Set global log level
    container[LoggingSettings].log_level = "DEBUG"
    logger = container[LoggingConfig].get_logger("Main")

    logger.info("Starting main")
    service = container[ExampleService]
    sample = container[AnotherSample]
    asyncio.run(service.do_something())
    sample.do_something()
    logger.info("Finished main, Run API Service")
    container[SocketService].run(main_process=False)
    container[APIService].run(main_process=True)


if __name__ == "__main__":
    main()
