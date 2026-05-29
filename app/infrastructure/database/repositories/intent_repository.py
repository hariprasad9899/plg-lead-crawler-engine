from sqlalchemy.orm import Session as SQLAlchemySession
from pydantic import EmailStr


class IntentRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db
    
    