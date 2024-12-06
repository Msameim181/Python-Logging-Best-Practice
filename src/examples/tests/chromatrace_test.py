import asyncio
import threading

import injection  # noqa
import pytest
from adaptors.socket_client import SocketClient, SocketClientConfig
from chromatrace import LoggingConfig
from dependency import container
from frameworks.api_app import APIService
from frameworks.socket_app import SocketService
from usecases.example_service import ExampleService, InnerService
from usecases.sample import AnotherSample


class TestChromatrace:
    @pytest.fixture(scope="class")
    def logging_config(self):
        return container[LoggingConfig]

    @pytest.fixture(scope="class")
    def socket_client_config(self):
        return SocketClientConfig()

    @pytest.fixture(scope="class")
    def api_service(self, logging_config):
        return container[APIService]

    @pytest.fixture(scope="class")
    def socket_service(self):
        return container[SocketService]

    @pytest.mark.asyncio
    def test_socket_service(self, socket_service):
        assert socket_service is not None

    @pytest.fixture(scope="class")
    def socket_client(self, socket_client_config):
        return SocketClient(config=socket_client_config)

    @pytest.mark.asyncio
    async def test_socket_client(self, socket_client, socket_service):
        assert socket_client is not None
        th = threading.Thread(
            target=socket_client.start_background_loop,
            args=(socket_client.client_loop,),
            daemon=True,
        )
        th.start()
        asyncio.run_coroutine_threadsafe(socket_client.run(), socket_client.client_loop)
        await asyncio.sleep(1)  # Allow time for the client to start
        th.join(timeout=1)  # Wait for thread to finish or timeout

    @pytest.mark.asyncio
    def test_api_service(self, api_service):
        assert api_service is not None
        assert api_service.logger is not None
        assert api_service.rest_application is not None

    @pytest.mark.asyncio
    async def test_example_service(self, logging_config):
        inner_service = InnerService(logging_config)
        example_service = ExampleService(logging_config, inner_service)
        assert example_service is not None
        await example_service.do_something()

    @pytest.mark.asyncio
    async def test_another_sample(self, logging_config):
        another_sample = AnotherSample(logging_config)
        assert another_sample is not None
        another_sample.do_something()
        await another_sample.consume()
        await another_sample.send_http_request_with_trace_id()
