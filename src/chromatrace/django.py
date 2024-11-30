from django.http import HttpRequest

from .tracer import RequestIdContext, trace_id_ctx


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request_id = request.headers.get("X-Request-ID")
        with RequestIdContext(request_id):
            response = self.get_response(request)
            response["X-Request-ID"] = trace_id_ctx.get()
            return response
