from sqlalchemy.orm import Session as SQLAlchemySession
from pydantic import EmailStr
from app.infrastructure.database.models.intent_job import IntentJob
from typing import Optional
from dataclasses import asdict


class JobConfigRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db

    def create_job_config(self, data):
        self.db.add(data)
        self.db.flush()
        return data
