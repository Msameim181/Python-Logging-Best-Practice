# Chromatrace

Chromatrace is a Python package designed for advanced logging capabilities, including trace and request ID management. It provides a flexible logging configuration and supports colored logging for better visibility.

## Features

- Configurable logging settings using Pydantic.
- Support for trace IDs and request IDs.
- Customizable log formats and handlers.
- Asynchronous and synchronous function tracing.

## Installation

You can install Chromatrace via pip:

```bash
pip install chromatrace
```

## Usage

To use Chromatrace in your application, you can import the necessary components:

```python
from chromatrace import LoggingSettings, LoggingConfig, tracer
```

Configure your logging settings:

```python
logging_config = LoggingConfig(
    settings=LoggingSettings(), 
    application_level='Development', 
    enable_tracing=True, 
    ignore_nan_trace=True
)
logger = logging_config.get_logger(__name__)
```

Use the `tracer` decorator to trace your functions:

```python
@tracer
async def my_async_function():
    # Your code here
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.