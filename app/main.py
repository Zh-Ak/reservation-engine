import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.dependencies.db import SessionDep
from app.exceptions import AppError
from app.routes.auth import router as auth_router
from app.routes.bookings import router as bookings_router
from app.routes.properties import router as properties_router
from app.routes.rooms import router as rooms_router
from app.routes.search import router as search_router
from app.routes.users import router as users_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("app")

app = FastAPI(title="Reservation Engine")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(properties_router)
app.include_router(rooms_router)
app.include_router(search_router)
app.include_router(bookings_router)


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=headers)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "%s %s -> %s in %.1f ms request_id=%s",
        request.method, request.url.path, response.status_code, duration_ms, request_id,
    )
    return response


@app.get("/health")
async def health(session: SessionDep):
    await session.execute(text("SELECT 1"))
    return {"status": "OK"}