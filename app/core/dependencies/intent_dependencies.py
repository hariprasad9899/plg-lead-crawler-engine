from fastapi import Depends
from app.core.config import settings
from app.infrastructure.database.sessions import get_db

def get_auth_service(db=Depends(get_db)):
    pass
