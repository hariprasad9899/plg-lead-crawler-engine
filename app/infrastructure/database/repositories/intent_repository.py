from sqlalchemy.orm import Session as SQLAlchemySession
from pydantic import EmailStr
from app.infrastructure.database.models.intent_job import IntentJob
from app.core.schemas.intents_schemas import IntentJobCreate
from typing import Optional
from dataclasses import asdict

class IntentRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db
    
    def create_intent(self,data: IntentJobCreate):
        db_obj = IntentJob(**asdict(data))
        self.db.add(db_obj)
        self.db.flush()
        return db_obj
    
    
    