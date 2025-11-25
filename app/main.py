# app/main.py

from fastapi import FastAPI
from sqlalchemy import text

from app.config.settings import get_settings
from app.config.connection import SessionLocal
from app.observability.metrics import metrics_middleware
from app.observability.tracing import init_tracing


def create_app() -> FastAPI:
    settings = get_settings()



    # Optional tracing
    if settings.enable_tracing:
        init_tracing()

    app = FastAPI(title=settings.app_name)


    # ----------------------------------------------------
    # 🚀 STARTUP EVENT — TEST DB CONNECTION
    # ----------------------------------------------------
    @app.on_event("startup")
    async def startup_db_check():
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            print(" DATABASE CONNECTED — PostgreSQL + pgvector is reachable")
            db.close()
        except Exception as e:
            print(" DATABASE CONNECTION FAILED")
            print(e)
            raise e
    # ----------------------------------------------------


    # Routers
    from app.api.v1.routes_query import router as query_router
    from app.api.v1.routes_health import router as health_router
    from app.api.v1.routes_ingestion import router as ingestion_router
    from app.api.v1.routes_metrics import router as metrics_router

    app.include_router(health_router, prefix="/v1")
    app.include_router(query_router, prefix="/v1")
    app.include_router(ingestion_router, prefix="/v1")
    app.include_router(metrics_router)  # /metrics at root

    # Metrics middleware
    if settings.enable_metrics:
        app.middleware("http")(metrics_middleware)

    return app


app = create_app()
