from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.config import settings
from app.core.logger import get_logger

logger = get_logger("main")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG
    )

    # ---------------------------
    # CORS CONFIGURATION
    # ---------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------------------------
    # ROUTES
    # ---------------------------
    app.include_router(router)

    # ---------------------------
    # STARTUP EVENT
    # ---------------------------
    @app.on_event("startup")
    async def startup_event():
        logger.info("Server starting...")
        logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
        logger.info(f"Allowed Origins: {settings.ALLOWED_ORIGINS}")

    # ---------------------------
    # SHUTDOWN EVENT
    # ---------------------------
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Server shutting down...")

    return app


app = create_app()