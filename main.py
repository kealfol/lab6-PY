import logging
from time import perf_counter

from fastapi import FastAPI, Request

from app.config import Settings
from app.logging_config import configure_logging
from app.routers import items

configure_logging()
logger = logging.getLogger("lab6.requests")
settings = Settings()
app = FastAPI(
    title=settings.app_name,
    description="Лабораторная работа по FastAPI",
    version="1.0.0",
    contact={"name": "Студент", "email": settings.admin_email},
)
app.include_router(items.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("%s %s -> 500", request.method, request.url.path)
        raise
    elapsed_ms = (perf_counter() - started) * 1000
    level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(
        level, "%s %s -> %s (%.2f ms)",
        request.method, request.url.path, response.status_code, elapsed_ms,
    )
    return response


@app.get("/", summary="Главная страница")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/info", summary="Настройки приложения")
def get_info():
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_page": settings.items_per_page,
    }
