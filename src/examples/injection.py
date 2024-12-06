from lagom import Singleton
from src.chromatrace import LoggingSettings

from .api_app import APIService
from .dependency import container
from .socket_app import SocketService

container[LoggingSettings] = LoggingSettings(
    application_level="Development",
    enable_tracing=True,
    ignore_nan_trace=False,
    enable_file_logging=False,
)
container[APIService] = Singleton(APIService)
container[SocketService] = Singleton(SocketService)
