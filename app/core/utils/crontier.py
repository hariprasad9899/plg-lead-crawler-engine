from croniter import croniter
from datetime import datetime, timezone
from app.core.exceptions.error_catalog import INVALID_SCHEDULE_EXPRESSION
from app.core.exceptions.base import AppException

def compute_timestamp_from_cron(cron_expression: str) -> datetime:
    if not croniter.is_valid(cron_expression):
        raise AppException(INVALID_SCHEDULE_EXPRESSION)
    return croniter(cron_expression, datetime.now(timezone.utc)).get_next(datetime)