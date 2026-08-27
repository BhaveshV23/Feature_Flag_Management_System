import fnmatch

from app.api.flag_routes import create_targeting_rule, update_flag
from app.schemas.feat_flag import FlagUpdate
from app.schemas.targeting_rule import TargetingRuleCreate
from app.services import evaluation_engine
from app.services.evaluation_engine import evaluate_flag
from app.core.security import AuthenticatedUser


class FakeRedis:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value

    def scan_iter(self, match=None, count=None):
        yield from [key for key in list(self.values) if fnmatch.fnmatchcase(key, match)]

    def delete(self, *keys):
        deleted = 0
        for key in keys:
            if key in self.values:
                del self.values[key]
                deleted += 1
        return deleted


def test_flag_update_invalidates_all_context_specific_evaluations(db_session, monkeypatch):
    cache = FakeRedis()
    monkeypatch.setattr(evaluation_engine, "redis_client", cache)

    first = evaluate_flag(db_session, "dark_mode", "development", {"user_id": "one"})
    evaluate_flag(db_session, "dark_mode", "development", {"user_id": "two"})
    cached = evaluate_flag(db_session, "dark_mode", "development", {"user_id": "one"})
    assert cached["message"] == "Returned From Redis Cache"

    flag = db_session.query(evaluation_engine.Flag).filter_by(key="dark_mode").first()
    update_flag(
        flag.id,
        FlagUpdate(
            key="dark_mode",
            type=flag.type,
            default_value=flag.default_value,
            enabled=False,
            description=flag.description,
            owner_team=flag.owner_team,
        ),
        db_session,
        AuthenticatedUser(user_id=1, username="tester"),
    )

    second = evaluate_flag(db_session, "dark_mode", "development", {"user_id": "one"})
    assert first["enabled"] is True
    assert second["enabled"] is False
    assert second["message"] == "Default Flag Evaluation"


def test_targeting_rule_change_invalidates_only_its_flag_cache(db_session, monkeypatch):
    cache = FakeRedis()
    monkeypatch.setattr(evaluation_engine, "redis_client", cache)

    context = {"user_id": "targeted-user"}
    initial = evaluate_flag(db_session, "dark_mode", "development", context)
    evaluate_flag(db_session, "payment_v2", "development", context)

    dark_mode = db_session.query(evaluation_engine.Flag).filter_by(key="dark_mode").first()
    create_targeting_rule(
        TargetingRuleCreate(
            flag_id=dark_mode.id,
            rule_type="user",
            operator="equals",
            value="targeted-user",
        ),
        db_session,
        AuthenticatedUser(user_id=1, username="tester"),
    )

    changed = evaluate_flag(db_session, "dark_mode", "development", context)
    unrelated = evaluate_flag(db_session, "payment_v2", "development", context)

    assert initial["message"] == "Default Flag Evaluation"
    assert changed["message"] == "Matched User Targeting Rule"
    assert unrelated["message"] == "Returned From Redis Cache"
