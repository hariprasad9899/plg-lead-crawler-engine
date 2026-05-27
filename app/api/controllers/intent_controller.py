from fastapi import APIRouter, Depends, BackgroundTasks, Request, Response
from app.core.utils.response import success_response
from app.core.utils.env_config import Settings
from app.core.exceptions.error_catalog import (
    USER_NOT_FOUND,
    UNAUTHORIZED,
    SESSION_NOT_FOUND,
)

router = APIRouter(prefix="/intents", tags=["Intents"])
settings = Settings()

@router.get("/get-intent")
def get_intents():
    data = {
        "intents": [ {"intent1": True }]
    }
    return success_response(data=data)