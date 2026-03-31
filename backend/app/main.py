from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.routers.allowlist import router as allowlist_router
from app.routers.auth import router as auth_router
from app.routers.shifts import router as shifts_router
from app.routers.users import router as users_router

app = FastAPI(title=settings.APP_NAME, version="0.3.0")

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


app.include_router(auth_router)
app.include_router(shifts_router)
app.include_router(allowlist_router)
app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "ok"}
