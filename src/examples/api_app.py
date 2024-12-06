import multiprocessing

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.chromatrace import LoggingConfig
from src.chromatrace.fastapi import RequestIdMiddleware

from .example_service import ExampleService
from .sample import AnotherSample


class APIService:
    def __init__(
        self,
        logging_config: LoggingConfig,
        example_service: ExampleService,
        another_sample: AnotherSample,
    ):
        self.logger = logging_config.get_logger(self.__class__.__name__)
        self.rest_application = FastAPI()

        self.example_service = example_service
        self.another_sample = another_sample

        # Add middleware
        self.rest_application.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allows all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allows all methods
            allow_headers=["*"],  # Allows all headers
        )
        self.rest_application.add_middleware(RequestIdMiddleware)

        self.do_something()
        self.routes()

    def do_something(self):
        self.logger.debug("Check something in API service")
        self.logger.info("Doing something in API service")
        self.logger.error("Something went wrong in API service")

    def run(self, main_process: bool = True):
        self.logger.info("Starting API Endpoint...")
        if main_process:
            uvicorn.run(
                self.rest_application,  # could be "main:api_app" for worker, auto reload
                host="0.0.0.0",
                port=8000,
                log_level="info",
                # factory=True, # if using "main:api_app" will required
            )
        else:
            self.rest_api_process = multiprocessing.Process(
                target=uvicorn.run,
                kwargs={
                    "app": self.rest_application,  # could be "main:api_app" for worker, auto reload
                    "host": "0.0.0.0",
                    "port": 8000,
                    "log_level": "info",
                    # "factory": True,  # if using "main:api_app" will required
                },
            ).start()

    def routes(self):
        @self.rest_application.get("/")
        async def read_root():
            self.logger.info("Hello World")
            await self.example_service.do_something()
            return {"message": "Hello World"}

        @self.rest_application.get("/consume")
        async def consume():
            await self.another_sample.consume()
            return {"message": "Consuming"}

        @self.rest_application.get("/send_http_request")
        async def send_http_request():
            await self.another_sample.send_http_request_with_trace_id()
            return {"message": "Sending HTTP request"}
