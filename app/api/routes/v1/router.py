from fastapi import APIRouter
from app.api.controllers.intent_controller import router as intent_router

router = APIRouter(prefix="/api/v1")
router.include_router(intent_router)