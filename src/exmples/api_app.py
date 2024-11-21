from example_service import ExampleService
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from chromatrace import LoggingConfig, RequestIdContext, trace_id_ctx


class APIService:
    def __init__(self, logging_config: LoggingConfig, example_service: ExampleService):
        self.logger = logging_config.get_logger(self.__class__.__name__)
        self.app = FastAPI()
        self.example_service = example_service
        # Add middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allows all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allows all methods
            allow_headers=["*"],  # Allows all headers
        )

        class RequestIdMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                request_id = request.headers.get("X-Request-ID")
                with RequestIdContext(request_id):
                    response = await call_next(request)
                    response.headers["X-Request-ID"] = trace_id_ctx.get()
                    return response

        self.app.add_middleware(RequestIdMiddleware)
        self.do_something()
        self.routes()
    
    def do_something(self):
        self.logger.debug("Check something in API service")
        self.logger.info("Doing something in API service")
        self.logger.error("Something went wrong in API service")

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8000,)

    def routes(self):

        @self.app.get("/")
        async def read_root():
            self.logger.info("Hello World")
            await self.example_service.do_something()
            return {"message": "Hello World"}
