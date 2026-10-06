from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import AppError
from app.routes.users import router as users_router
from app.routes.auth import router as auth_router

app = FastAPI(title="Reservation Engine")

app.include_router(auth_router)
app.include_router(users_router)


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=headers)


@app.get("/health")
async def health():
    return {"status":"OK"}