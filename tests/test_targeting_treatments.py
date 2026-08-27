from app.api.flag_routes import create_targeting_rule, update_targeting_rule
from app.core.security import AuthenticatedUser
from app.models.audit_log import AuditLog
from app.models.flag import Flag
from app.models.targeting_rule import TargetingRule
from app.models.user_group_membership import UserGroupMembership
from app.schemas.targeting_rule import TargetingRuleCreate, TargetingRuleUpdate
from app.services.evaluation_engine import evaluate_flag


def actor():
    return AuthenticatedUser(user_id=1, username="tester")


def flag(db_session, key):
    return db_session.query(Flag).filter_by(key=key).first()


def add_rule(db_session, flag_id, rule_type, *, value=None, percentage=None, enabled=True, is_active=True, priority=1):
    rule = TargetingRule(flag_id=flag_id, priority=priority, rule_type=rule_type, operator="equals" if rule_type != "percentage" else None, value=value, percentage=percentage, enabled=enabled, is_active=is_active)
    db_session.add(rule)
    db_session.commit()
    return rule


def evaluate(db_session, key, user_context=None):
    return evaluate_flag(db_session, key, "development", user_context)


def test_active_user_rules_apply_enabled_treatment(db_session):
    add_rule(db_session, flag(db_session, "payment_v2").id, "user", value="on", enabled=True)
    add_rule(db_session, flag(db_session, "dark_mode").id, "user", value="off", enabled=False)

    assert evaluate(db_session, "payment_v2", {"user_id": "on"})["enabled"] is True
    assert evaluate(db_session, "dark_mode", {"user_id": "off"})["enabled"] is False


def test_inactive_rule_is_ignored(db_session):
    add_rule(db_session, flag(db_session, "payment_v2").id, "user", value="user", enabled=True, is_active=False)

    result = evaluate(db_session, "payment_v2", {"user_id": "user"})
    assert result["message"] == "Default Flag Evaluation"
    assert result["enabled"] is False


def test_group_and_percentage_rules_apply_treatment(db_session):
    payment = flag(db_session, "payment_v2")
    dark_mode = flag(db_session, "dark_mode")
    db_session.add(UserGroupMembership(user_id="member", group_name="beta"))
    db_session.commit()
    add_rule(db_session, payment.id, "group", value="beta", enabled=True)
    add_rule(db_session, dark_mode.id, "percentage", percentage=100, enabled=False)

    assert evaluate(db_session, "payment_v2", {"user_id": "member"})["enabled"] is True
    assert evaluate(db_session, "dark_mode", {"user_id": "any"})["enabled"] is False


def test_percentage_boundaries_and_determinism(db_session):
    payment = flag(db_session, "payment_v2")
    dark_mode = flag(db_session, "dark_mode")
    add_rule(db_session, payment.id, "percentage", percentage=0, enabled=True)
    add_rule(db_session, dark_mode.id, "percentage", percentage=50, enabled=False)

    assert evaluate(db_session, "payment_v2", {"user_id": "any"})["enabled"] is False
    assert evaluate(db_session, "payment_v2")["enabled"] is False
    first = evaluate(db_session, "dark_mode", {"user_id": "same-user"})
    second = evaluate(db_session, "dark_mode", {"user_id": "same-user"})
    assert second["message"] == "Returned From Redis Cache"
    assert first["enabled"] is second["enabled"]


def test_treatment_change_invalidates_cache_and_audit_snapshot_includes_activation(db_session):
    dark_mode = flag(db_session, "dark_mode")
    rule = create_targeting_rule(TargetingRuleCreate(flag_id=dark_mode.id, rule_type="user", operator="equals", value="user", enabled=True, is_active=True), db_session, actor())
    context = {"user_id": "user"}
    assert evaluate(db_session, "dark_mode", context)["enabled"] is True

    update_targeting_rule(rule.id, TargetingRuleUpdate(flag_id=dark_mode.id, priority=1, rule_type="user", operator="equals", value="user", percentage=None, enabled=False, is_active=True), db_session, actor())
    assert evaluate(db_session, "dark_mode", context)["enabled"] is False
    audit_record = db_session.query(AuditLog).order_by(AuditLog.id.desc()).first()
    assert audit_record.new_state["is_active"] is True

    update_targeting_rule(rule.id, TargetingRuleUpdate(flag_id=dark_mode.id, priority=1, rule_type="user", operator="equals", value="user", percentage=None, enabled=False, is_active=False), db_session, actor())
    assert evaluate(db_session, "dark_mode", context)["enabled"] is True
