from .tracer import RequestIdContext


class SocketRequestIdMiddleware:
    def __init__(self, app, prefix: str = "S-"):
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))
        trace_id = headers.get(b"x-trace-id", None)
        if trace_id:
            trace_id = trace_id.decode("utf-8")
        with RequestIdContext(trace_id, self.prefix):
            await self.app(scope, receive, send)
