import asyncio
import sys

from chromatrace import LoggingConfig, LoggingSettings, trace

import injection  # noqa
from api_app import APIService
from dependency import container
from example_service import ExampleService
from sample import AnotherSample

sys.stdout.reconfigure(encoding='utf-8')
app = container[APIService].app

@trace
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
    
    container[APIService].run()

if __name__ == "__main__":
    main()