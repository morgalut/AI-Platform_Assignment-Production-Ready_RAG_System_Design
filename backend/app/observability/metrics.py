# app/observability/metrics.py

import time
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


# ---------------------------------------------------------
#   Prometheus metric definitions
# ---------------------------------------------------------

REQUEST_LATENCY = Histogram(
    "rag_http_request_latency_seconds",
    "Latency of HTTP requests in seconds.",
    ["method", "path", "status"],
)

REQUEST_COUNT = Counter(
    "rag_http_requests_total",
    "Total number of HTTP requests.",
    ["method", "path", "status"],
)

OPERATOR_LATENCY = Histogram(
    "rag_operator_latency_seconds",
    "Latency of ORC operators in seconds.",
    ["operator"],
)

OPERATOR_ERRORS = Counter(
    "rag_operator_errors_total",
    "Total number of ORC operator errors.",
    ["operator"],
)


# ---------------------------------------------------------
#   FastAPI Middleware
# ---------------------------------------------------------

async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to record latency & request count for every HTTP call.
    """
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start

    method = request.method
    path = request.url.path
    status = str(response.status_code)

    REQUEST_LATENCY.labels(method=method, path=path, status=status).observe(elapsed)
    REQUEST_COUNT.labels(method=method, path=path, status=status).inc()

    return response


# ---------------------------------------------------------
#   /metrics endpoint helper
# ---------------------------------------------------------

def prometheus_fastapi_handler():
    """
    Returns data for /metrics endpoint.
    """
    data = generate_latest()
    return data, CONTENT_TYPE_LATEST
