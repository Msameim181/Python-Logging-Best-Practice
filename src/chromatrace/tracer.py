import asyncio
import contextvars
import functools
import logging
import uuid
from typing import Optional

trace_id_ctx = contextvars.ContextVar("trace_id", default=None)

class TraceContext:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or f"T-{str(uuid.uuid4())[:8]}"
        self.token = None

    def __enter__(self):
        self.token = trace_id_ctx.set(self.trace_id)
        return self
    
    def __exit__(self, *args):
        trace_id_ctx.reset(self.token)

    async def __aenter__(self):
        self.token = trace_id_ctx.set(self.trace_id)
        return self

    async def __aexit__(self, *args):
        trace_id_ctx.reset(self.token)

def tracer(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        async with TraceContext():
            return await func(*args, **kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        with TraceContext():
            return func(*args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

class RequestIdContext:
    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or f"R-{str(uuid.uuid4())[:8]}"
        self.token = None

    def __enter__(self):
        self.token = trace_id_ctx.set(self.request_id)
        return self

    def __exit__(self, *args):
        trace_id_ctx.reset(self.token)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = trace_id_ctx.get() or "NAN"
        return True