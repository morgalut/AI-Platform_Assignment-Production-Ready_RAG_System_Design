# app/api/v1/routes_metrics.py

from fastapi import APIRouter, Response
from app.observability.metrics import prometheus_fastapi_handler

router = APIRouter()


@router.get("/metrics")
def metrics_endpoint():
    data, content_type = prometheus_fastapi_handler()
    return Response(content=data, media_type=content_type)
