from datetime import datetime, timezone

import redis

from app.services.evaluation_analytics import (
    evaluation_bucket_key,
    evaluation_field,
    record_evaluation,
    utc_hour_start,
)


class AnalyticsRedis:
    def __init__(self):
        self.hashes = {}

    def hincrby(self, key, field, amount):
        bucket = self.hashes.setdefault(key, {})
        bucket[field] = bucket.get(field, 0) + amount
        return bucket[field]


class UnavailableRedis:
    def hincrby(self, *_args):
        raise redis.exceptions.ConnectionError("Redis unavailable")


def test_record_evaluation_increments_same_utc_hour_counter():
    cache = AnalyticsRedis()
    timestamp = datetime(2026, 8, 29, 14, 37, tzinfo=timezone.utc)

    assert record_evaluation(cache, 7, 3, timestamp) == 1
    assert record_evaluation(cache, 7, 3, timestamp) == 2
    assert cache.hashes[evaluation_bucket_key(timestamp)][evaluation_field(7, 3)] == 2


def test_counters_separate_flags_and_environments():
    cache = AnalyticsRedis()
    timestamp = datetime(2026, 8, 29, 14, tzinfo=timezone.utc)
    key = evaluation_bucket_key(timestamp)

    record_evaluation(cache, 7, 3, timestamp)
    record_evaluation(cache, 8, 3, timestamp)
    record_evaluation(cache, 7, 4, timestamp)

    assert cache.hashes[key] == {"3:7": 1, "3:8": 1, "4:7": 1}


def test_different_utc_hours_use_different_buckets():
    cache = AnalyticsRedis()
    first = datetime(2026, 8, 29, 14, 59, tzinfo=timezone.utc)
    second = datetime(2026, 8, 29, 15, 0, tzinfo=timezone.utc)

    record_evaluation(cache, 7, 3, first)
    record_evaluation(cache, 7, 3, second)

    assert utc_hour_start(first).hour == 14
    assert evaluation_bucket_key(first) != evaluation_bucket_key(second)


def test_naive_timestamp_is_interpreted_as_utc():
    timestamp = datetime(2026, 8, 29, 14, 37)
    assert utc_hour_start(timestamp).tzinfo == timezone.utc
    assert evaluation_bucket_key(timestamp).endswith("2026082914")


def test_analytics_redis_failure_is_isolated(caplog):
    with caplog.at_level("WARNING", logger="app.services.evaluation_analytics"):
        result = record_evaluation(UnavailableRedis(), 7, 3, datetime.now(timezone.utc))

    assert result is None
    assert "Evaluation analytics counter unavailable" in caplog.text
