from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .tracer import RequestIdContext, trace_id_ctx


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        with RequestIdContext(request_id):
            response = await call_next(request)
            response.headers["X-Request-ID"] = trace_id_ctx.get()
            return response