from chromatrace import LoggingSettings
from dependency import container
from frameworks.api_app import APIService
from frameworks.socket_app import SocketService
from lagom import Singleton

container[LoggingSettings] = LoggingSettings(
    application_level="Development",
    enable_tracing=True,
    ignore_nan_trace=False,
    enable_file_logging=True,
)
container[APIService] = Singleton(APIService)
container[SocketService] = Singleton(SocketService)