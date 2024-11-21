import logging

from chromatrace import LoggingConfig


class SecondService:
    def __init__(self, logging_config: LoggingConfig):
        self.logger = logging_config.get_logger(self.__class__.__name__)
        self.logger.setLevel(logging.ERROR)
    
    async def do_something(self):
        self.logger.debug("Check something in second service")
        self.logger.info("Doing something in second service")
        self.logger.error("Something went wrong in second service")


class ExampleService:
    def __init__(self, logging_config: LoggingConfig, second_service: SecondService):
        self.logger = logging_config.get_logger(self.__class__.__name__)
        self.second_service = second_service
        self.logger.setLevel(logging.ERROR)
    
    async def do_something(self):
        self.logger.debug("Check something")
        self.logger.info("Doing something")
        self.logger.error("Something went wrong")
        await self.second_service.do_something()

