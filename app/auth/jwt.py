import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import SESSION_EXPIRED, INVALID_SESSION
from app.core.utils.env_config import settings


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms="HS256")
        if payload.get("type") != "access":
            raise AppException(INVALID_SESSION)
        return payload
    except ExpiredSignatureError:
        raise AppException(SESSION_EXPIRED)
    except InvalidTokenError:
        raise AppException(INVALID_SESSION)
