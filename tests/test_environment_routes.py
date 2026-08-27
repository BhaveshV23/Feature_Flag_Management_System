import pytest
from fastapi import HTTPException
from test_auth import client
from app.services.auth_service import create_access_token

from app.api.flag_routes import (
    create_environment,
    delete_environment,
    get_environment_by_id,
    update_environment,
)
from app.core.security import AuthenticatedUser
from app.models.audit_log import AuditLog
from app.models.environment import Environment
from app.models.flag import Flag
from app.models.flag_version import FlagVersion
from app.models.targeting_rule import TargetingRule
from app.schemas.environment import CreateEnvironment, UpdateEnvironment


def actor():
    return AuthenticatedUser(user_id=1, username="tester")


def test_environment_endpoints_require_authentication(client):
    token = create_access_token({"sub": "admin", "user_id": 1})
    assert client("GET", "/api/environment", headers={"Authorization": f"Bearer {token}"})["status"] == 200
    for method, path, body in [
        ("GET", "/api/environment/1", None),
        ("POST", "/api/environment", {"name": "new", "description": None, "is_active": True}),
        ("PUT", "/api/environment/1", {"name": "new", "description": None, "is_active": True}),
        ("DELETE", "/api/environment/1", None),
    ]:
        assert client(method, path, body=body)["status"] == 401


def error_status(call, *args):
    with pytest.raises(HTTPException) as exc:
        call(*args)
    return exc.value.status_code


def test_environment_retrieval_statuses(db_session):
    environment = db_session.query(Environment).first()
    assert get_environment_by_id(environment.id, db_session).id == environment.id
    assert error_status(get_environment_by_id, 999, db_session) == 404


def test_environment_create_validation_and_duplicate(db_session):
    assert create_environment(CreateEnvironment(name="staging", description="Stage", is_active=True), db_session).name == "staging"
    for name in ("", "   ", "x" * 51):
        with pytest.raises(Exception):
            CreateEnvironment(name=name, is_active=True)
    assert error_status(create_environment, CreateEnvironment(name="development", is_active=True), db_session) == 409
    assert db_session.query(Environment).filter_by(name="development").count() == 1


def test_environment_update_and_duplicate_safety(db_session):
    environment = db_session.query(Environment).first()
    update_environment(environment.id, UpdateEnvironment(name="renamed", description="Updated", is_active=False), db_session)
    db_session.refresh(environment)
    assert environment.name == "renamed" and environment.is_active is False
    assert error_status(update_environment, 999, UpdateEnvironment(name="x", is_active=True), db_session) == 404
    for name in ("", "   ", "x" * 51):
        with pytest.raises(Exception):
            UpdateEnvironment(name=name, is_active=True)
    other = Environment(name="other", is_active=True)
    db_session.add(other)
    db_session.commit()
    assert error_status(update_environment, environment.id, UpdateEnvironment(name="other", is_active=True), db_session) == 409
    db_session.refresh(environment)
    assert environment.name == "renamed"


def test_environment_rename_preserves_flags_and_invalidates_old_namespace(db_session, monkeypatch):
    environment = db_session.query(Environment).first()
    keys = [flag.key for flag in environment.flags]
    calls = []
    monkeypatch.setattr("app.api.flag_routes.invalidate_flag_cache_safely", lambda name, key: calls.append((name, key)))
    update_environment(environment.id, UpdateEnvironment(name="renamed", is_active=True), db_session)
    assert calls == [("development", key) for key in keys]
    assert all(flag.environment_id == environment.id for flag in environment.flags)


def test_environment_rename_does_not_invalidate_unrelated_environment(db_session, monkeypatch):
    other = Environment(name="other", is_active=True)
    db_session.add(other)
    db_session.commit()
    calls = []
    monkeypatch.setattr("app.api.flag_routes.invalidate_flag_cache_safely", lambda name, key: calls.append((name, key)))
    update_environment(1, UpdateEnvironment(name="renamed", is_active=True), db_session)
    assert all(name == "development" for name, _ in calls)


def test_environment_rename_with_redis_failure_still_commits(db_session, monkeypatch):
    monkeypatch.setattr("app.services.evaluation_engine.invalidate_flag_cache", lambda *_: (_ for _ in ()).throw(OSError("Redis unavailable")))
    environment = db_session.query(Environment).first()
    update_environment(environment.id, UpdateEnvironment(name="renamed", is_active=True), db_session)
    db_session.refresh(environment)
    assert environment.name == "renamed"


def test_environment_delete_empty_and_missing(db_session):
    empty = Environment(name="empty", is_active=True)
    db_session.add(empty)
    db_session.commit()
    delete_environment(empty.id, db_session)
    assert db_session.get(Environment, empty.id) is None
    assert error_status(delete_environment, 999, db_session) == 404


@pytest.mark.parametrize("dependency", ["one_flag", "multiple_flags", "targeting_rule", "version", "audit"])
def test_environment_delete_rejects_dependencies_and_preserves_data(db_session, dependency):
    environment = Environment(name=f"blocked-{dependency}", is_active=True)
    db_session.add(environment)
    db_session.flush()
    flags = []
    if dependency in {"one_flag", "multiple_flags", "targeting_rule", "version"}:
        flags.append(Flag(environment_id=environment.id, key="one", name="One", type="boolean", default_value="false", enabled=False, description="", owner_team="team"))
        if dependency == "multiple_flags":
            flags.append(Flag(environment_id=environment.id, key="two", name="Two", type="boolean", default_value="false", enabled=False, description="", owner_team="team"))
        db_session.add_all(flags)
        db_session.flush()
        if dependency == "targeting_rule":
            db_session.add(TargetingRule(flag_id=flags[0].id, rule_type="user", operator="equals", value="u", enabled=True, is_active=True))
        if dependency == "version":
            db_session.add(FlagVersion(flag_id=flags[0].id, version=1, enabled=True, config={}))
    if dependency == "audit":
        db_session.add(AuditLog(environment_id=environment.id, actor="tester", action="TEST"))
    db_session.commit()
    assert error_status(delete_environment, environment.id, db_session) == 409
    assert db_session.get(Environment, environment.id) is not None
    assert db_session.query(Flag).filter_by(environment_id=environment.id).count() == len(flags)
    assert db_session.query(TargetingRule).join(Flag).filter(Flag.environment_id == environment.id).count() == (1 if dependency == "targeting_rule" else 0)
    assert db_session.query(FlagVersion).join(Flag).filter(Flag.environment_id == environment.id).count() == (1 if dependency == "version" else 0)
