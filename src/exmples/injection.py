from dependency import container

from chromatrace import LoggingConfig, LoggingSettings

container[LoggingSettings] = LoggingSettings()
container[LoggingConfig] = LoggingConfig(
    container[LoggingSettings], 
    application_level='Development', 
    enable_tracing=True, 
    ignore_nan_trace=True
)