from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app.models.evaluation_count import EvaluationCount
from app.services.evaluation_analytics import evaluation_bucket_key, evaluation_field
from app.services.evaluation_analytics_flush import flush_completed_buckets


class FlushRedis:
    def __init__(self):
        self.hashes = {}
        self.values = {"flag:development:dark_mode:cached": "keep"}
        self.deleted = []
        self.fail_delete = False

    def scan_iter(self, match=None):
        yield from list(self.hashes) + list(self.values)

    def hgetall(self, key):
        return self.hashes[key]

    def delete(self, *keys):
        if self.fail_delete:
            raise OSError("Redis unavailable")
        self.deleted.extend(keys)
        for key in keys:
            self.hashes.pop(key, None)
            self.values.pop(key, None)
        return len(keys)


def hour(day=29, hour=14):
    return datetime(2026, 8, day, hour, tzinfo=timezone.utc)


def test_flushes_completed_bucket_and_deletes_after_commit(db_session):
    cache = FlushRedis()
    key = evaluation_bucket_key(hour())
    cache.hashes[key] = {evaluation_field(1, 1): "7"}

    assert flush_completed_buckets(db_session, cache, hour(29, 15)) == 1
    row = db_session.query(EvaluationCount).one()
    assert row.evaluation_count == 7
    assert row.hour_start.replace(tzinfo=timezone.utc) == hour()
    assert key in cache.deleted
    assert "flag:development:dark_mode:cached" in cache.values


def test_current_hour_is_not_flushed(db_session):
    cache = FlushRedis()
    key = evaluation_bucket_key(hour(29, 15))
    cache.hashes[key] = {evaluation_field(1, 1): "3"}

    assert flush_completed_buckets(db_session, cache, hour(29, 15)) == 0
    assert db_session.query(EvaluationCount).count() == 0
    assert key not in cache.deleted


def test_multiple_buckets_and_fields_are_persisted(db_session):
    cache = FlushRedis()
    first = evaluation_bucket_key(hour(29, 12))
    second = evaluation_bucket_key(hour(29, 13))
    cache.hashes[first] = {"1:1": "2", "1:2": "4"}
    cache.hashes[second] = {"2:1": "5"}

    assert flush_completed_buckets(db_session, cache, hour(29, 14)) == 2
    assert sorted(row.evaluation_count for row in db_session.query(EvaluationCount).all()) == [2, 4, 5]


def test_repeating_flush_is_idempotent(db_session):
    cache = FlushRedis()
    key = evaluation_bucket_key(hour())
    cache.hashes[key] = {"1:1": "9"}

    flush_completed_buckets(db_session, cache, hour(29, 15))
    cache.hashes[key] = {"1:1": "9"}
    flush_completed_buckets(db_session, cache, hour(29, 15))
    assert db_session.query(EvaluationCount).one().evaluation_count == 9


def test_malformed_data_keeps_bucket_but_persists_valid_records(db_session, caplog):
    cache = FlushRedis()
    key = evaluation_bucket_key(hour())
    cache.hashes[key] = {"1:1": "4", "bad": "not-a-count"}

    flush_completed_buckets(db_session, cache, hour(29, 15))
    assert db_session.query(EvaluationCount).one().evaluation_count == 4
    assert key not in cache.deleted
    assert "malformed" in caplog.text


def test_redis_delete_failure_does_not_undo_commit(db_session, caplog):
    cache = FlushRedis()
    key = evaluation_bucket_key(hour())
    cache.hashes[key] = {"1:1": "6"}
    cache.fail_delete = True

    flush_completed_buckets(db_session, cache, hour(29, 15))
    assert db_session.query(EvaluationCount).one().evaluation_count == 6
    assert "persisted but could not be deleted" in caplog.text


def test_database_failure_rolls_back_and_keeps_bucket(db_session, monkeypatch):
    cache = FlushRedis()
    key = evaluation_bucket_key(hour())
    cache.hashes[key] = {"1:1": "6"}
    original_commit = db_session.commit

    def failing_commit():
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(db_session, "commit", failing_commit)
    flush_completed_buckets(db_session, cache, hour(29, 15))
    monkeypatch.setattr(db_session, "commit", original_commit)
    assert db_session.query(EvaluationCount).count() == 0
    assert key not in cache.deleted
