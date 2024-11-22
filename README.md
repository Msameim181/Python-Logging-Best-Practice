# Chromatrace

Chromatrace is a Python package designed for advanced logging capabilities, including trace and request ID management. It provides a flexible logging configuration and supports colored logging for better visibility.

I believe that logging is an essential part of any application, and it is crucial to have a well-organized and structured logging system. Chromatrace aims to provide a simple and easy-to-use logging system that can be integrated into any Python application.
In simple terms, Chromatrace is a Best Practice of Logging in Python.

## Features

- Configurable logging settings using Pydantic.
- Customizable log levels and loggers for different services.
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
   logger.debug("Check something")
   logger.info("Doing something")
   logger.warning("Doing something")
   logger.error("Something went wrong")
```

### Dependency Injection using Lagom

```python
from lagom import Container

container = Container()

from chromatrace import LoggingConfig, LoggingSettings

container[LoggingSettings] = LoggingSettings()
container[LoggingConfig] = LoggingConfig(
    container[LoggingSettings], 
    application_level='Development', 
    enable_tracing=True, 
    ignore_nan_trace=True
)
```

Then, add the `LoggingConfig` to your service:

```python
import logging

from chromatrace import LoggingConfig


class SomeService:
    def __init__(self, logging_config: LoggingConfig):
        self.logger = logging_config.get_logger(self.__class__.__name__)
        self.logger.setLevel(logging.ERROR)
    
    async def do_something(self):
        self.logger.debug("Check something in second service")
        self.logger.info("Doing something in second service")
        self.logger.error("Something went wrong in second service")
```

Results:
```log
[Development]-(2024-11-21 23:43:26)-[INFO]-[APIService]-FILENAME:api_app.py-FUNC:do_something-THREAD:MainThread-LINE:27 :: 
Doing something in API service

[Development]-(2024-11-21 23:43:26)-[ERROR]-[APIService]-FILENAME:api_app.py-FUNC:do_something-THREAD:MainThread-LINE:28 :: 
Something went wrong in API service

[T-dc1be4de]-[Development]-(2024-11-21 23:43:26)-[INFO]-[Main]-FILENAME:main.py-FUNC:main-THREAD:MainThread-LINE:21 :: 
Starting main

[T-dc1be4de]-[Development]-(2024-11-21 23:43:26)-[ERROR]-[ExampleService]-FILENAME:example_service.py-FUNC:do_something-THREAD:MainThread-LINE:26 :: 
Something went wrong

[T-dc1be4de]-[Development]-(2024-11-21 23:43:26)-[INFO]-[InnerService]-FILENAME:example_service.py-FUNC:do_something-THREAD:MainThread-LINE:13 :: 
Doing something in second service

[T-dc1be4de]-[Development]-(2024-11-21 23:43:26)-[ERROR]-[InnerService]-FILENAME:example_service.py-FUNC:do_something-THREAD:MainThread-LINE:14 :: 
Something went wrong in second service

[T-dc1be4de]-[Development]-(2024-11-21 23:43:26)-[DEBUG]-[AnotherSample]-FILENAME:sample.py-FUNC:do_something-THREAD:MainThread-LINE:12 :: 
Check something

[T-dc1be4de]-[Development]-(2024-11-21 23:43:26)-[INFO]-[AnotherSample]-FILENAME:sample.py-FUNC:do_something-THREAD:MainThread-LINE:13 :: 
Doing something

[T-dc1be4de]-[Development]-(2024-11-21 23:43:26)-[WARNING]-[AnotherSample]-FILENAME:sample.py-FUNC:do_something-THREAD:MainThread-LINE:14 :: 
Doing something

[T-dc1be4de]-[Development]-(2024-11-21 23:43:26)-[ERROR]-[AnotherSample]-FILENAME:sample.py-FUNC:do_something-THREAD:MainThread-LINE:15 :: 
Something went wrong
```

The two first log was out of trace and the trace ID was not added to the log message. The rest of the logs were within the trace and the trace ID - `T-dc1be4de`, was added to the log message.

**NOTE**: The important thing is that each Class or Service can have its own log level. This is useful when you want to have different log levels for different services.

### FastAPI Integration

```python
from chromatrace import RequestIdMiddleware

app = FastAPI()
app.add_middleware(RequestIdMiddleware)
```

Result:
```log
[R-ffe0a9a2]-[Development]-(2024-11-22 00:13:53)-[INFO]-[APIService]-FILENAME:api_app.py-FUNC:read_root-THREAD:MainThread-LINE:38 :: 
Hello World

[R-ffe0a9a2]-[Development]-(2024-11-22 00:13:53)-[ERROR]-[ExampleService]-FILENAME:example_service.py-FUNC:do_something-THREAD:MainThread-LINE:26 :: 
Something went wrong

[R-ffe0a9a2]-[Development]-(2024-11-22 00:13:53)-[INFO]-[InnerService]-FILENAME:example_service.py-FUNC:do_something-THREAD:MainThread-LINE:13 :: 
Doing something in second service

[R-ffe0a9a2]-[Development]-(2024-11-22 00:13:53)-[ERROR]-[InnerService]-FILENAME:example_service.py-FUNC:do_something-THREAD:MainThread-LINE:14 :: 
Something went wrong in second service
```

As you can see, the request ID - `R-ffe0a9a2` is automatically added to the log messages from the thread that handles the request.


## Examples

You can find examples of how to use Chromatrace in the [examples](src/exmples/) directory. Run the examples using the following command:

```bash
python main.py
```

Then, run:
    
```bash
curl 0.0.0.0:8000
```

Now, check the logs in the terminal. :)

## License

This project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE - see the [LICENSE](LICENSE) file for details.

## Ideas and Sources

- [Python Logging Best Practices Tips](https://coralogix.com/blog/python-logging-best-practices-tips/)
- [12 Python Logging Best Practices To Debug Apps Faster](https://middleware.io/blog/python-logging-best-practices/)
- [10 Best Practices for Logging in Python](https://betterstack.com/community/guides/logging/python/python-logging-best-practices/)