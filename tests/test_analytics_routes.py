from datetime import datetime, timedelta, timezone

import pytest

from app.api.analytics_routes import get_evaluation_analytics
from app.models.evaluation_count import EvaluationCount
from app.services.auth_service import create_access_token
from test_auth import auth_header, client


def utc_hour(day, hour):
    return datetime(2026, 8, day, hour, tzinfo=timezone.utc)


def seed_counts(db_session):
    rows = [
        EvaluationCount(flag_id=1, environment_id=1, hour_start=utc_hour(20, 10), evaluation_count=10),
        EvaluationCount(flag_id=2, environment_id=1, hour_start=utc_hour(20, 10), evaluation_count=20),
        EvaluationCount(flag_id=1, environment_id=2, hour_start=utc_hour(20, 11), evaluation_count=30),
        EvaluationCount(flag_id=1, environment_id=1, hour_start=utc_hour(20, 12), evaluation_count=40),
    ]
    db_session.add_all(rows)
    db_session.commit()


def test_authenticated_analytics_request_returns_array(client, db_session):
    token = create_access_token({"sub": "admin", "user_id": 1})
    response = client("GET", "/api/analytics/evaluations", headers=auth_header(token))
    assert response["status"] == 200
    assert isinstance(response["json"], list)


def test_analytics_route_requires_authentication(client):
    response = client("GET", "/api/analytics/evaluations")
    assert response["status"] == 401


def test_analytics_filters_and_ordering(db_session):
    seed_counts(db_session)
    rows = get_evaluation_analytics(db_session, flag_id=1, environment_id=1, start=utc_hour(20, 10), end=utc_hour(20, 13))
    assert [(row.hour_start.hour, row.evaluation_count) for row in rows] == [(10, 10), (12, 40)]


def test_analytics_end_is_exclusive_and_start_inclusive(db_session):
    seed_counts(db_session)
    rows = get_evaluation_analytics(db_session, flag_id=None, environment_id=None, start=utc_hour(20, 10), end=utc_hour(20, 12))
    assert [row.hour_start.hour for row in rows] == [10, 10, 11]


def test_analytics_empty_and_unknown_filters_return_empty(db_session):
    seed_counts(db_session)
    assert get_evaluation_analytics(db_session, flag_id=999999, environment_id=None, start=None, end=None) == []
    assert get_evaluation_analytics(db_session, flag_id=None, environment_id=999999, start=None, end=None) == []
    assert get_evaluation_analytics(db_session, flag_id=None, environment_id=None, start=utc_hour(21, 0), end=utc_hour(21, 1)) == []


@pytest.mark.parametrize("start,end", [(utc_hour(20, 10), utc_hour(20, 10)), (utc_hour(20, 11), utc_hour(20, 10))])
def test_analytics_rejects_invalid_date_range(db_session, start, end):
    with pytest.raises(Exception) as error:
        get_evaluation_analytics(db_session, flag_id=None, environment_id=None, start=start, end=end)
    assert getattr(error.value, "status_code", None) == 422


def test_analytics_one_sided_ranges_are_bounded(db_session):
    seed_counts(db_session)
    end = utc_hour(20, 12)
    rows = get_evaluation_analytics(db_session, flag_id=None, environment_id=None, start=None, end=end)
    assert len(rows) == 3
    start = utc_hour(20, 10)
    rows = get_evaluation_analytics(db_session, flag_id=None, environment_id=None, start=start, end=start + timedelta(hours=2))
    assert len(rows) == 3
