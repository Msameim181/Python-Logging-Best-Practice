import logging
import multiprocessing

import socketio
import uvicorn
from chromatrace import (
    GetLoggingConfig,
    LoggingConfig,
    SocketRequestIdMiddleware,
    UvicornLoggingSettings,
)


class SocketServerConfig:
    def __init__(
        self,
    ):
        self.log_level = "debug"
        self.cors_allowed_origins = "*"
        self.socketio_path = "/socket.io"
        self.logger = False
        self.engineio_logger = False
        self.always_connect = True


class SocketService:
    def __init__(
        self,
        socket_config: SocketServerConfig,
        logging_config: LoggingConfig,
    ) -> None:
        self.socket_config = socket_config
        self.logger = logging_config.get_logger("Socket")
        self.logger.setLevel(logging.DEBUG)
        self.create_socket()
        self.call_backs()

    def create_socket(self):
        self.sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=self.socket_config.cors_allowed_origins,
            always_connect=self.socket_config.always_connect,
            logger=self.logger if self.socket_config.logger else False,
            engineio_logger=self.logger
            if self.socket_config.engineio_logger
            else False,
        )
        self.socket_application = socketio.ASGIApp(
            socketio_server=self.sio,
            socketio_path=self.socket_config.socketio_path,
        )
        self.socket_application = SocketRequestIdMiddleware(self.socket_application)

    def run(self, main_process: bool = True):
        self.logger.info("Starting Socket Service...")
        if main_process:
            uvicorn.run(
                self.socket_application,
                host="0.0.0.0",
                port=8001,
                log_level="info",
                log_config=GetLoggingConfig(
                    UvicornLoggingSettings(
                        enable_file_logging=True,
                        show_process_id=True,
                    )
                ),
            )
        else:
            self.rest_api_process = multiprocessing.Process(
                target=uvicorn.run,
                kwargs={
                    "app": self.socket_application,
                    "host": "0.0.0.0",
                    "port": 8001,
                    "log_level": "info",
                    "log_config": GetLoggingConfig(
                        UvicornLoggingSettings(
                            enable_file_logging=True,
                            show_process_id=True,
                        )
                    ),
                },
            ).start()

    def call_backs(self):
        @self.sio.on(event="connect", namespace="/")
        async def connect(sid, environ, auth):
            self.logger.info("Socket connected on main namespace. SID: %s", sid)

        @self.sio.on(event="message", namespace="/")
        async def message(sid, data: dict):
            self.logger.info(
                "Received message on main namespace. SID: %s, Message: %s", sid, data
            )
            await self.sio.emit("message", "Hearing you, clearly.", room=sid)

        @self.sio.on(event="connect", namespace="/sample")
        async def sample_connect(sid, environ, auth):
            headers = environ.get("asgi.scope").get("headers")
            headers = {k.decode(): v.decode() for k, v in dict(headers).items()}
            self.logger.info(f"Socket connected on `sample` namespace. SID: {sid}")

        @self.sio.on(event="message", namespace="/sample")
        async def sample_message(sid, data: dict):
            self.logger.info(
                "Received message on main namespace. SID: %s, Message: %s", sid, data
            )
            await self.sio.emit(
                "message", "Hearing you, again, clearly.", room=sid, namespace="/sample"
            )
