import os
from pathlib import Path


class Settings:
    # ---------------------------
    # CORE APP CONFIG
    # ---------------------------
    APP_NAME: str = os.getenv("APP_NAME", "IoT Sensor Server")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # ---------------------------
    # SERVER CONFIG
    # ---------------------------
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # ---------------------------
    # SECURITY
    # ---------------------------
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "CHANGE_THIS_IN_PRODUCTION_please_use_env"
    )

    # ---------------------------
    # STORAGE
    # ---------------------------
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / os.getenv("DATA_DIR", "data")

    # ---------------------------
    # LIMITS
    # ---------------------------
    MAX_RECORDS_PER_DEVICE: int = int(
        os.getenv("MAX_RECORDS_PER_DEVICE", 500)
    )

    # ---------------------------
    # CORS (for frontend)
    # ---------------------------
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS",
        "*"
    ).split(",")


settings = Settings()