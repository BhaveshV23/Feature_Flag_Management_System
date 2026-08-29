from datetime import datetime, timezone
import logging

import redis


logger = logging.getLogger(__name__)

ANALYTICS_KEY_PREFIX = "analytics:evaluations:"


def utc_hour_start(timestamp: datetime | None = None) -> datetime:
    """Return the UTC hour bucket for a timestamp."""

    value = timestamp or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.replace(minute=0, second=0, microsecond=0)


def evaluation_bucket_key(timestamp: datetime | None = None) -> str:
    return f"{ANALYTICS_KEY_PREFIX}{utc_hour_start(timestamp):%Y%m%d%H}"


def evaluation_field(flag_id: int, environment_id: int) -> str:
    return f"{environment_id}:{flag_id}"


def record_evaluation(redis_client, flag_id: int, environment_id: int, timestamp: datetime | None = None) -> int | None:
    """Atomically increment one flag/environment hourly evaluation counter.

    Telemetry is best effort: Redis failures are logged and never propagated to
    the caller, so evaluation behavior remains independent of analytics.
    """

    key = evaluation_bucket_key(timestamp)
    field = evaluation_field(flag_id, environment_id)
    try:
        return redis_client.hincrby(key, field, 1)
    except (redis.exceptions.RedisError, OSError) as exc:
        logger.warning(
            "Evaluation analytics counter unavailable for flag %s/environment %s: %s",
            flag_id,
            environment_id,
            exc,
        )
        return None
