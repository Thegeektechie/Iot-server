from fastapi import APIRouter
from app.api.v1 import sensor, dashboard, stream, config, records, decrypt

router = APIRouter()

router.include_router(sensor.router, prefix="/api/v1")
router.include_router(stream.router, prefix="/api/v1")
router.include_router(records.router, prefix="/api/v1")
router.include_router(decrypt.router, prefix="/api/v1")
router.include_router(dashboard.router)
router.include_router(config.router, prefix="/api")
