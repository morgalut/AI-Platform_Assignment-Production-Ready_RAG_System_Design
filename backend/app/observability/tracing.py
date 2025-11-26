# app/observability/tracing.py

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.config.settings import get_settings

settings = get_settings()


def init_tracing() -> None:
    """
    Initialize OpenTelemetry tracing with a simple console exporter.
    In production, swap ConsoleSpanExporter for OTLP/Jaeger/etc.
    """
    resource = Resource(attributes={"service.name": settings.app_name})

    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
