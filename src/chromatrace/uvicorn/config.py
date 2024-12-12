from pathlib import Path
from typing import Optional

from pydantic import BaseModel

__all__ = ["GetLoggingConfig", "UvicornLoggingSettings"]


class UvicornLoggingSettings(BaseModel):
    log_level: str = "INFO"
    file_path: Path = Path("./log/uvicorn_app.log")
    max_bytes: int = 500 * 1024 * 1024  # 500MB
    backup_count: int = 3  # 3 days retention
    syslog_host: Optional[str] = None
    syslog_port: Optional[int] = None
    enable_console_logging: bool = True
    enable_file_logging: bool = False
    use_console_colored_formatter: bool = True
    use_syslog_colored_formatter: bool = False
    use_file_colored_formatter: bool = False
    show_process_id: bool = False

    def __init__(self, **data):
        super().__init__(**data)
        if self.enable_file_logging:
            if isinstance(self.file_path, str):
                self.file_path = Path(self.file_path)
            if isinstance(self.file_path, Path):
                self.file_path.parent.mkdir(parents=True, exist_ok=True)


def GetLoggingConfig(logging_settings: UvicornLoggingSettings):
    default_fmt = "[%(levelname)s]: %(message)s"
    access_fmt = '[%(levelname)s]: ADDRESS:(%(client_address)s) - REQUEST:"%(request_detail)s" - STATUS:%(status_detail)s'
    if logging_settings.show_process_id:
        default_fmt = "(%(asctime)s)-[%(process)s]-" + default_fmt
        access_fmt = "(%(asctime)s)-[%(process)s]-" + access_fmt
    else:
        default_fmt = "(%(asctime)s)-" + default_fmt
        access_fmt = "(%(asctime)s)-" + access_fmt
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "chromatrace.uvicorn.formatters.DefaultFormatter",
                "fmt": default_fmt,
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": True,
            },
            "colorless_default": {
                "()": "chromatrace.uvicorn.formatters.DefaultFormatter",
                "fmt": default_fmt,
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": False,
            },
            "access": {
                "()": "chromatrace.uvicorn.formatters.AccessFormatter",
                "fmt": access_fmt,
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": True,
            },
            "colorless_access": {
                "()": "chromatrace.uvicorn.formatters.AccessFormatter",
                "fmt": access_fmt,
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": False,
            },
        },
        "handlers": {},
        "loggers": {
            "uvicorn": {"handlers": [], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": [], "level": "INFO"},
            "uvicorn.access": {
                "handlers": [],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    if logging_settings.enable_console_logging:
        config = {
            "formatter": "",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        }
        access_config = config.copy()
        config["formatter"] = "colorless_default"
        access_config["formatter"] = "colorless_access"
        if logging_settings.use_console_colored_formatter:
            config["formatter"] = "default"
            access_config["formatter"] = "access"
        LOGGING_CONFIG["handlers"]["default"] = config
        LOGGING_CONFIG["handlers"]["access"] = access_config
        LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"].append("default")
        LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"].append("access")
    if logging_settings.enable_file_logging:
        config = {
            "formatter": "",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(logging_settings.file_path),
            "maxBytes": logging_settings.max_bytes,
            "backupCount": logging_settings.backup_count,
            "encoding": "utf-8",
        }
        access_config = config.copy()
        config["formatter"] = "colorless_default"
        access_config["formatter"] = "colorless_access"
        if logging_settings.use_file_colored_formatter:
            config["formatter"] = "default"
            access_config["formatter"] = "access"
        LOGGING_CONFIG["handlers"]["access_file"] = access_config
        LOGGING_CONFIG["handlers"]["access_file_default"] = config
        LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"].append("access_file_default")
        LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"].append("access_file")
    if logging_settings.syslog_host and logging_settings.syslog_port:
        config = {
            "formatter": "colorless_default",
            "class": "logging.handlers.SysLogHandler",
            "address": (logging_settings.syslog_host, logging_settings.syslog_port),
        }
        config["formatter"] = "colorless_access"
        if logging_settings.use_syslog_colored_formatter:
            config["formatter"] = "access"
        LOGGING_CONFIG["handlers"]["syslog"] = config
        LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"].append("syslog")

    return LOGGING_CONFIG
