from pydantic import BaseModel
from uuid import UUID


class AuthContext(BaseModel):
    user_id: UUID
    tenant_id: UUID
