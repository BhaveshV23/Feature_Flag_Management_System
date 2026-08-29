from datetime import datetime, timezone
import logging
import re

import redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.evaluation_count import EvaluationCount


logger = logging.getLogger(__name__)

BUCKET_PATTERN = re.compile(r"^analytics:evaluations:(\d{10})$")


def _utc_hour(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


def bucket_hour(bucket_key: str) -> datetime | None:
    """Parse an analytics bucket key into its UTC hour, or return None."""

    match = BUCKET_PATTERN.fullmatch(bucket_key)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y%m%d%H").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def completed_bucket_keys(redis_client, now: datetime | None = None) -> list[tuple[str, datetime]]:
    """Return valid analytics buckets strictly before the current UTC hour."""

    current_hour = _utc_hour(now or datetime.now(timezone.utc))
    keys: list[tuple[str, datetime]] = []
    for raw_key in redis_client.scan_iter(match="analytics:evaluations:*"):
        key = raw_key.decode() if isinstance(raw_key, bytes) else str(raw_key)
        hour = bucket_hour(key)
        if hour is not None and hour < current_hour:
            keys.append((key, hour))
    return sorted(set(keys), key=lambda item: item[0])


def _parse_hash_fields(values: dict) -> tuple[list[tuple[int, int, int]], bool]:
    records: list[tuple[int, int, int]] = []
    malformed = False
    for raw_field, raw_count in values.items():
        field = raw_field.decode() if isinstance(raw_field, bytes) else str(raw_field)
        count_value = raw_count.decode() if isinstance(raw_count, bytes) else raw_count
        try:
            environment_id, flag_id = field.split(":")
            environment_id = int(environment_id)
            flag_id = int(flag_id)
            count = int(count_value)
            if environment_id <= 0 or flag_id <= 0 or count < 0:
                raise ValueError
        except (TypeError, ValueError):
            malformed = True
            logger.warning("Skipping malformed evaluation analytics counter field %r", field)
            continue
        records.append((environment_id, flag_id, count))
    return records, malformed


def flush_completed_buckets(db: Session, redis_client, now: datetime | None = None) -> int:
    """Persist completed Redis analytics buckets and remove them after commit.

    Existing rows are overwritten with the bucket's authoritative count, making
    retries after a crash idempotent rather than additive.
    """

    flushed = 0
    for key, hour_start in completed_bucket_keys(redis_client, now):
        try:
            values = redis_client.hgetall(key)
        except (redis.exceptions.RedisError, OSError) as exc:
            logger.warning("Unable to read evaluation analytics bucket %s: %s", key, exc)
            continue

        records, malformed = _parse_hash_fields(values)
        if not records:
            if malformed:
                logger.warning("Retaining evaluation analytics bucket %s because it contains no valid records", key)
            else:
                try:
                    redis_client.delete(key)
                except (redis.exceptions.RedisError, OSError) as exc:
                    logger.warning("Unable to delete empty evaluation analytics bucket %s: %s", key, exc)
            continue

        try:
            for environment_id, flag_id, count in records:
                row = (
                    db.query(EvaluationCount)
                    .filter_by(flag_id=flag_id, environment_id=environment_id, hour_start=hour_start)
                    .first()
                )
                if row is None:
                    db.add(EvaluationCount(flag_id=flag_id, environment_id=environment_id, hour_start=hour_start, evaluation_count=count))
                else:
                    row.evaluation_count = count
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            logger.exception("Failed to persist evaluation analytics bucket %s; retaining Redis data", key)
            continue

        if malformed:
            logger.warning("Retaining evaluation analytics bucket %s because malformed fields were found", key)
            flushed += 1
            continue

        try:
            redis_client.delete(key)
            flushed += 1
        except (redis.exceptions.RedisError, OSError) as exc:
            logger.warning("Evaluation analytics bucket %s persisted but could not be deleted: %s", key, exc)
            flushed += 1

    return flushed
