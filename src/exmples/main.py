import sys

import injection  # noqa
from dependency import container
from example_service import ExampleService
from chromatrace import LoggingConfig, LoggingSettings, tracer
from api_app import APIService
from sample import Sample
import asyncio

sys.stdout.reconfigure(encoding='utf-8')
app = container[APIService].app

@tracer
def main():
    # Optional: Set global log level
    container[LoggingSettings].log_level = "DEBUG"
    logger = container[LoggingConfig].get_logger("Main")

    logger.info("Starting main")
    service = container[ExampleService]
    sample = container[Sample]
    asyncio.run(service.do_something())
    sample.do_something()
    logger.info("Finished main, Run API Service")
    
    container[APIService].run()

if __name__ == "__main__":
    main()