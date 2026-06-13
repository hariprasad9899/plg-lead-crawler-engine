from fastapi import Depends
from .schemas import AuthContext
from app.auth.jwt import verify_token
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import UNAUTHORIZED

bearer_scheme = HTTPBearer()


def get_auth_context(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> AuthContext:
    # try cookie first (browser)
    token = request.cookies.get("access_token")

    # fallback to bearer header
    if not token:
        if not credentials:
            raise AppException(UNAUTHORIZED)
        token = credentials.credentials

    payload = verify_token(token)
    return AuthContext(user_id=payload["user_id"], tenant_id=payload["tenant_id"])
