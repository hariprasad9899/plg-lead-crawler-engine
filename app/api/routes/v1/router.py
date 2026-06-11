from fastapi import APIRouter
from app.api.controllers.intent_controller import router as intent_router
from app.api.controllers.job_config_controller import router as job_config_router

router = APIRouter(prefix="/api/v1")
router.include_router(intent_router)
router.include_router(job_config_router)
