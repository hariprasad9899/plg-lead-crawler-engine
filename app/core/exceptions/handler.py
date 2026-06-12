from fastapi import Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.base import AppException
from app.core.utils.response import error_response
import logging

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException):

    return error_response(
        code=exc.error.code,
        message=exc.error.message,
        status_code=exc.error.status_code,
        details=exc.details,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = [
        {
            "field": ".".join(map(str, err["loc"])),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]

    return error_response(
        code="VALIDATION_ERROR",
        message="Validation failed",
        status_code=422,
        details=details,
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return error_response(
        code="DATABASE_CONFLICT",
        message="Database conflict occured",
        status_code=409,
    )


async def generic_exeption_handler(request: Request, exc: Exception):
    logger.exception(exc)
    return error_response(
        code="INTERNAL_SERVER_ERROR",
        message="Something went wrong",
        status_code=500,
    )
