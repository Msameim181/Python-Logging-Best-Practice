from dependency import container
from frameworks.api_app import APIService
from frameworks.socket_app import SocketService
from lagom import Singleton

from chromatrace import LoggingSettings

container[LoggingSettings] = LoggingSettings(
    application_level="Development",
    enable_tracing=True,
    ignore_nan_trace=True,
    enable_file_logging=True,
    show_process_id=True,
)
container[APIService] = Singleton(APIService)
container[SocketService] = Singleton(SocketService)
