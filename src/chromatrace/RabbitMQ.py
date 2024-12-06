from contextlib import contextmanager

import pika

from .tracer import RequestIdContext, trace_id_ctx


@contextmanager
def rabbitmq_trace_context(channel, properties):
    request_id = properties.headers.get("X-Request-ID") if properties.headers else None
    with RequestIdContext(request_id):
        yield
        if properties.headers is None:
            properties.headers = {}
        properties.headers["X-Request-ID"] = trace_id_ctx.get()

class RabbitMQMiddleware:
    def __init__(self, connection_parameters):
        self.connection = pika.BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()

    def publish(self, exchange, routing_key, body, properties=None):
        if properties is None:
            properties = pika.BasicProperties()
        with rabbitmq_trace_context(self.channel, properties):
            self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=properties)

    def consume(self, queue, on_message_callback, auto_ack=False):
        def callback(ch, method, properties, body):
            with rabbitmq_trace_context(ch, properties):
                on_message_callback(ch, method, properties, body)
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=auto_ack)
        self.channel.start_consuming()