import logging

from chromatrace import LoggingConfig


class Sample:
    def __init__(self, logging_config: LoggingConfig):
        self.logger = logging_config.get_logger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        
    def do_something(self):
        self.logger.debug("Check something")
        self.logger.info("Doing something")
        self.logger.warning("Doing something")
        self.logger.error("Something went wrong")