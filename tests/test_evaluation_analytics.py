from datetime import datetime, timezone

import redis

from app.services.evaluation_analytics import (
    evaluation_bucket_key,
    evaluation_field,
    record_evaluation,
    utc_hour_start,
)
from app.services import evaluation_engine


class AnalyticsRedis:
    def __init__(self):
        self.hashes = {}
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value

    def hincrby(self, key, field, amount):
        bucket = self.hashes.setdefault(key, {})
        bucket[field] = bucket.get(field, 0) + amount
        return bucket[field]


class UnavailableRedis:
    def get(self, *_args):
        return None

    def set(self, *_args):
        return None

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


def test_valid_evaluation_requests_are_counted_including_cache_hits(db_session, monkeypatch):
    cache = AnalyticsRedis()
    monkeypatch.setattr(evaluation_engine, "redis_client", cache)
    timestamp = datetime(2026, 8, 29, 14, tzinfo=timezone.utc)
    monkeypatch.setattr("app.services.evaluation_analytics.datetime", _FixedDateTime(timestamp))

    from app.services.evaluation_engine import evaluate_flag

    evaluate_flag(db_session, "dark_mode", "development", {"user_id": "same"})
    evaluate_flag(db_session, "dark_mode", "development", {"user_id": "same"})
    evaluate_flag(db_session, "dark_mode", "development", {"user_id": "same"})

    environment = db_session.query(evaluation_engine.Environment).filter_by(name="development").one()
    flag = db_session.query(evaluation_engine.Flag).filter_by(key="dark_mode").one()
    assert cache.hashes[evaluation_bucket_key(timestamp)][evaluation_field(flag.id, environment.id)] == 3


def test_invalid_evaluations_do_not_create_analytics_counters(db_session, monkeypatch):
    cache = AnalyticsRedis()
    monkeypatch.setattr(evaluation_engine, "redis_client", cache)
    from app.services.evaluation_engine import evaluate_flag

    assert evaluate_flag(db_session, "missing", "development")['success'] is False
    assert evaluate_flag(db_session, "dark_mode", "missing")['success'] is False
    assert cache.hashes == {}


def test_analytics_failure_does_not_change_evaluation_result(db_session, monkeypatch, caplog):
    monkeypatch.setattr(evaluation_engine, "redis_client", UnavailableRedis())
    from app.services.evaluation_engine import evaluate_flag

    with caplog.at_level("WARNING", logger="app.services.evaluation_analytics"):
        result = evaluate_flag(db_session, "dark_mode", "development", {"user_id": "same"})

    assert result["success"] is True
    assert result["enabled"] is True
    assert "Evaluation analytics counter unavailable" in caplog.text


class _FixedDateTime:
    def __init__(self, current):
        self.current = current

    def now(self, tz=None):
        return self.current.astimezone(tz) if tz else self.current.replace(tzinfo=None)
