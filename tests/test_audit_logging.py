import fnmatch

from app.api.flag_routes import create_flag, create_targeting_rule, delete_flag, delete_targeting_rule, update_flag, update_targeting_rule
from app.core.security import AuthenticatedUser
from app.models.audit_log import AuditLog
from app.models.flag import Flag
from app.models.targeting_rule import TargetingRule
from app.schemas.feat_flag import FlagCreate, FlagUpdate
from app.schemas.targeting_rule import TargetingRuleCreate, TargetingRuleUpdate
from app.services import evaluation_engine


class FakeRedis:
    def __init__(self): self.values = {}
    def get(self, key): return self.values.get(key)
    def set(self, key, value): self.values[key] = value
    def scan_iter(self, match=None, count=None): yield from [key for key in list(self.values) if fnmatch.fnmatchcase(key, match)]
    def delete(self, *keys):
        deleted = 0
        for key in keys:
            if key in self.values:
                self.values.pop(key)
                deleted += 1
        return deleted


def user(): return AuthenticatedUser(user_id=42, username="audit-admin")
def flag(db, key): return db.query(Flag).filter_by(key=key).first()
def records(db): return db.query(AuditLog).order_by(AuditLog.id).all()


def test_flag_mutations_create_actor_attributed_audit_diffs(db_session, monkeypatch):
    monkeypatch.setattr(evaluation_engine, "redis_client", FakeRedis())
    environment_id = flag(db_session, "dark_mode").environment_id
    created = create_flag(FlagCreate(environment_id=environment_id, key="audited", name="Audited", type="boolean", default_value="false", enabled=False, description="created", owner_team="platform"), db_session, user())
    update_flag(created.id, FlagUpdate(key="audited", type="boolean", default_value="false", enabled=True, description="updated", owner_team="platform"), db_session, user())
    update_flag(created.id, FlagUpdate(key="audited", type="boolean", default_value="false", enabled=False, description="updated", owner_team="platform"), db_session, user())
    delete_flag(created.id, db_session, user())

    create_record, enable_record, disable_record, delete_record = records(db_session)[-4:]
    assert (create_record.action, create_record.actor, create_record.environment_id) == ("CREATE", "audit-admin", environment_id)
    assert create_record.new_state["key"] == "audited"
    assert enable_record.action == "ENABLE"
    assert enable_record.old_state["enabled"] is False and enable_record.new_state["enabled"] is True
    assert disable_record.action == "DISABLE"
    assert delete_record.action == "DELETE" and delete_record.old_state["id"] == created.id


def test_flag_update_without_enable_change_records_update(db_session, monkeypatch):
    monkeypatch.setattr(evaluation_engine, "redis_client", FakeRedis())
    current = flag(db_session, "dark_mode")
    update_flag(current.id, FlagUpdate(key=current.key, type=current.type, default_value=current.default_value, enabled=True, description="new description", owner_team=current.owner_team), db_session, user())
    record = records(db_session)[-1]
    assert record.action == "UPDATE"
    assert record.old_state["description"] == "Enables dark mode UI"
    assert record.new_state["description"] == "new description"


def test_targeting_rule_mutations_record_complete_state_and_invalidate_both_flags(db_session, monkeypatch):
    cache = FakeRedis()
    monkeypatch.setattr(evaluation_engine, "redis_client", cache)
    dark_mode, payment = flag(db_session, "dark_mode"), flag(db_session, "payment_v2")
    rule = create_targeting_rule(TargetingRuleCreate(flag_id=dark_mode.id, priority=2, rule_type="user", operator="equals", value="one", percentage=None, enabled=True), db_session, user())
    cache.set("flag:development:dark_mode:one", "cached")
    cache.set("flag:development:payment_v2:one", "cached")
    update_targeting_rule(rule.id, TargetingRuleUpdate(flag_id=payment.id, priority=1, rule_type="user", operator="equals", value="two", percentage=None, enabled=False), db_session, user())
    assert cache.values == {}
    delete_targeting_rule(rule.id, db_session, user())

    create_record, update_record, delete_record = records(db_session)[-3:]
    assert create_record.action == "TARGETING_RULE_CREATE"
    assert create_record.new_state["environment_id"] == dark_mode.environment_id
    assert update_record.action == "TARGETING_RULE_UPDATE"
    assert update_record.old_state["flag_id"] == dark_mode.id
    assert update_record.new_state["flag_id"] == payment.id
    assert delete_record.action == "TARGETING_RULE_DELETE"
    assert delete_record.old_state["enabled"] is False
