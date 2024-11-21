from dependency import container
from logging_config import LoggingConfig
from logging_settings import LoggingSettings

container[LoggingSettings] = LoggingSettings()
container[LoggingConfig] = LoggingConfig(
    container[LoggingSettings], 
    application_level='Development', 
    enable_tracing=True, 
    ignore_nan_trace=True
)