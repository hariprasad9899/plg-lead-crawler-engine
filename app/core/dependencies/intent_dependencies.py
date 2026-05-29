from fastapi import Depends
from app.infrastructure.database.sessions.session import get_db
from app.infrastructure.database.repositories.intent_repository import IntentRepo
from app.core.services.intent_services import IntentService

def get_intent_service(db=Depends(get_db)):
    intent_repo = IntentRepo(db=db)
    return IntentService(intent_repo=intent_repo)
