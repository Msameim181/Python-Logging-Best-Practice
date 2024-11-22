from chromatrace import LoggingConfig, LoggingSettings

from dependency import container

container[LoggingSettings] = LoggingSettings(
    file_path="app.log"
)
container[LoggingConfig] = LoggingConfig(
    container[LoggingSettings], 
    application_level='Development', 
    enable_tracing=True, 
    ignore_nan_trace=True
)