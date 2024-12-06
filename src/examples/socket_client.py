import asyncio
import logging
import sys
import threading
import time
from typing import Dict, List, Optional

import socketio
from pydantic import BaseModel, Field
from src.chromatrace import LoggingConfig, LoggingSettings
from src.chromatrace.tracer import trace_id_ctx

logging_config = LoggingConfig(
    LoggingSettings(enable_tracing=True, file_path="app-client.log")
)
trace_id = "123456"
trace_id_ctx.set(f"C-{trace_id}")


class SocketClientConfig(BaseModel):
    server_url: str = "http://0.0.0.0:8001"
    namespaces: List[str] = ["/"]
    headers: Optional[Dict] = Field(default=None)
    socketio_path: str = "/socket.io"
    auth: Optional[Dict] = Field(default=None)
    logger: bool = False
    engineio_logger: bool = False
    reconnection: bool = True
    reconnection_delay: int = 3
    reconnection_attempts: int = 10


class SocketClient:
    def __init__(
        self,
        config: SocketClientConfig,
    ):
        self.logger = logging_config.get_logger(self.__class__.__name__)
        self.config = config
        self.logger.info("Initializing Socket Client to connect to the server.")
        self.logger.info(
            "Server URL: %s%s", self.config.server_url, self.config.socketio_path
        )
        self.sio = socketio.AsyncClient(
            handle_sigint=True,
            logger=self.logger if self.config.logger else False,
            engineio_logger=self.logger if self.config.engineio_logger else False,
            reconnection=self.config.reconnection,
            reconnection_delay=self.config.reconnection_delay,
            reconnection_attempts=self.config.reconnection_attempts,
        )

        self._client_loop = asyncio.new_event_loop()
        self.logger.info("Socket Client is initialized.")

    def start_background_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    @property
    def client_loop(self):
        return self._client_loop

    async def connect_to_server(self):
        try:
            self.logger.info("Connecting to the server...")
            await self.sio.connect(
                self.config.server_url,
                headers=self.config.headers,
                socketio_path=self.config.socketio_path,
                auth=self.config.auth,
                namespaces=self.config.namespaces,
            )
            self.logger.info("Connected to the server successfully.")
        except ConnectionError:
            self.logger.error("Connection failed.")
        await self.sio.wait()

    def call_backs(self):
        @self.sio.on("connect", namespace="/")
        async def connect():
            self.logger.info("Connection established to the server with handshake.")

        @self.sio.on("disconnect", namespace="/")
        def disconnect():
            self.logger.info("Server disconnected.")
            self.client_loop.stop()

        @self.sio.on("message", namespace="/")
        async def message(data):
            self.logger.info("Message from the server in `message` event: %s", data)

    async def run(self):
        self.call_backs()
        await self.connect_to_server()


def handle_user_input(base_client: SocketClient, logger: logging.Logger):
    while True:
        if not base_client.sio.connected:
            logger.info(
                "Client connection with server has been lost, exiting the client..."
            )
            sys.exit(1)

        time.sleep(0.5)  # to enhance showcase
        user_input = input('Enter a message (or "exit" to quit): ')
        try:
            if user_input.lower() == "exit":
                break
            else:
                asyncio.run_coroutine_threadsafe(
                    base_client.sio.emit(
                        event="message",
                        data={"message": user_input},
                        namespace="/",
                    ),
                    base_client.client_loop,
                )
        except KeyboardInterrupt:
            break


def create_client():
    token = "Bearer XXXXXXXXXXX"
    config = SocketClientConfig(
        headers={
            "authorization": token,
            "x-trace-id": trace_id,
        },
        auth={"Authorization": token},
    )
    base_client = SocketClient(config=config)

    # starting the client background loop
    th = threading.Thread(
        target=base_client.start_background_loop,
        args=(base_client.client_loop,),
        daemon=True,
    )
    th.start()

    return base_client


def main():
    logger = logging_config.get_logger(__name__)
    logger.info("Starting client...")
    base_client = create_client()

    # running the client in the background loop
    asyncio.run_coroutine_threadsafe(base_client.run(), base_client.client_loop)

    time.sleep(0.5)
    logger.info("Ready to check the connection status and sending messages...")
    handle_user_input(base_client, logger)

    logger.info("Connection is closing...")
    base_client.sio.disconnect()


if __name__ == "__main__":
    main()
