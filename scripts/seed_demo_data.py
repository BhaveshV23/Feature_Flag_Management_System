"""Idempotently add presentation data to an existing FlagFlow database."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.session import SessionLocal
from app.models import (
    AuditLog,
    Environment,
    Flag,
    FlagVersion,
    TargetingRule,
    UserGroupMembership,
)
from app.services.audit_service import flag_to_dict, targeting_rule_to_dict


ACTOR = "Bhavesh"


def find_flag(db, environment_id: int, key: str) -> Flag | None:
    return db.scalar(select(Flag).where(Flag.environment_id == environment_id, Flag.key == key))


def add_flags(db, environments: dict[str, Environment]) -> list[Flag]:
    definitions = [
        ("testing", "search_v2", "Search V2", "Improved search validation for the test suite.", False, "platform-team"),
        ("Quality Control", "fraud_review", "Fraud Review", "QA workflow for fraud-review decisions.", True, "security-team"),
        ("production", "invoice_export", "Invoice Export", "Allow customers to export billing invoices.", False, "payments-team"),
    ]
    added: list[Flag] = []
    for environment_name, key, name, description, enabled, owner_team in definitions:
        environment = environments[environment_name]
        if find_flag(db, environment.id, key) is not None:
            continue
        flag = Flag(
            environment_id=environment.id,
            key=key,
            name=name,
            description=description,
            enabled=enabled,
            type="boolean",
            default_value="true" if enabled else "false",
            owner_team=owner_team,
        )
        db.add(flag)
        added.append(flag)
    db.flush()
    return added


def add_memberships(db) -> int:
    definitions = [
        ("user_001", "support_agents"),
        ("user_002", "early_access"),
        ("user_003", "early_access"),
    ]
    added = 0
    for user_id, group_name in definitions:
        exists = db.scalar(select(UserGroupMembership).where(UserGroupMembership.user_id == user_id, UserGroupMembership.group_name == group_name))
        if exists is None:
            db.add(UserGroupMembership(user_id=user_id, group_name=group_name))
            added += 1
    db.flush()
    return added


def rule_exists(db, definition: dict) -> bool:
    candidates = db.scalars(select(TargetingRule).where(TargetingRule.flag_id == definition["flag_id"], TargetingRule.priority == definition["priority"], TargetingRule.rule_type == definition["rule_type"], TargetingRule.operator == definition["operator"], TargetingRule.percentage == definition["percentage"])).all()
    return any(candidate.value == definition["value"] for candidate in candidates)


def add_rules(db, flags: dict[tuple[str, str], Flag], environments: dict[str, Environment]) -> list[TargetingRule]:
    def flag(environment_name: str, key: str) -> Flag:
        return flags[(environment_name, key)]

    definitions = [
        (flag("testing", "search_v2"), 1, "user", "equals", "user_001", None, True, True),
        (flag("production", "invoice_export"), 1, "group", "equals", "premium_users", None, True, True),
        (flag("Quality Control", "fraud_review"), 1, "percentage", None, None, 10, True, True),
        (flag("production", "new_checkout"), 2, "percentage", None, None, 75, False, True),
        (flag("staging", "recommendation_engine"), 2, "group", "equals", "early_access", None, False, False),
        (flag("testing", "search_v2"), 2, "user", "equals", "user_003", None, False, True),
    ]
    added: list[TargetingRule] = []
    for target_flag, priority, rule_type, operator, value, percentage, enabled, is_active in definitions:
        definition = {"flag_id": target_flag.id, "priority": priority, "rule_type": rule_type, "operator": operator, "value": value, "percentage": percentage}
        if rule_exists(db, definition):
            continue
        rule = TargetingRule(**definition, enabled=enabled, is_active=is_active)
        db.add(rule)
        added.append(rule)
    db.flush()
    return added


def add_versions(db, flags: list[Flag]) -> int:
    added = 0
    for flag in flags:
        existing = db.scalar(select(FlagVersion).where(FlagVersion.flag_id == flag.id, FlagVersion.version == 1))
        if existing is None:
            db.add(FlagVersion(flag_id=flag.id, version=1, enabled=flag.enabled, config={"source": "demo-seed", "default_value": flag.default_value}))
            added += 1
    db.flush()
    return added


def audit_exists(db, *, flag_id: int, environment_id: int, action: str, old_state: dict | None, new_state: dict | None) -> bool:
    records = db.scalars(select(AuditLog).where(AuditLog.flag_id == flag_id, AuditLog.environment_id == environment_id, AuditLog.actor == ACTOR, AuditLog.action == action)).all()
    return any(record.old_state == old_state and record.new_state == new_state for record in records)


def add_audit_logs(db, flags: dict[tuple[str, str], Flag], rules: list[TargetingRule]) -> int:
    flag_events = [
        ("development", "new_dashboard", "CREATE", None, True, 6),
        ("staging", "new_checkout", "UPDATE", False, True, 5),
        ("production", "premium_features", "DISABLE", True, False, 4),
        ("production", "premium_features", "ENABLE", False, True, 3),
        ("Quality Control", "fraud_review", "CREATE", None, True, 2),
        ("production", "invoice_export", "UPDATE", False, False, 1),
    ]
    added = 0
    now = datetime.now(timezone.utc)
    for environment_name, key, action, old_enabled, new_enabled, days_ago in flag_events:
        target = flags[(environment_name, key)]
        current = flag_to_dict(target)
        old_state = None if old_enabled is None else {**current, "enabled": old_enabled, "default_value": "true" if old_enabled else "false"}
        new_state = {**current, "enabled": new_enabled, "default_value": "true" if new_enabled else "false"}
        if audit_exists(db, flag_id=target.id, environment_id=target.environment_id, action=action, old_state=old_state, new_state=new_state):
            continue
        db.add(AuditLog(flag_id=target.id, environment_id=target.environment_id, actor=ACTOR, action=action, old_state=old_state, new_state=new_state, created_at=now - timedelta(days=days_ago)))
        added += 1

    for index, rule in enumerate(rules[:6]):
        environment_id = rule.flag.environment_id
        snapshot = targeting_rule_to_dict(rule, environment_id)
        action = ("TARGETING_RULE_CREATE", "TARGETING_RULE_UPDATE", "TARGETING_RULE_DELETE")[index % 3]
        old_state = None if action == "TARGETING_RULE_CREATE" else snapshot
        new_state = snapshot if action != "TARGETING_RULE_DELETE" else None
        if audit_exists(db, flag_id=rule.flag_id, environment_id=environment_id, action=action, old_state=old_state, new_state=new_state):
            continue
        db.add(AuditLog(flag_id=rule.flag_id, environment_id=environment_id, actor=ACTOR, action=action, old_state=old_state, new_state=new_state, created_at=now - timedelta(days=max(1, 6 - index))))
        added += 1
    return added


def seed() -> dict[str, int]:
    db = SessionLocal()
    try:
        environments = {environment.name: environment for environment in db.scalars(select(Environment)).all()}
        required = {"development", "testing", "staging", "production", "Quality Control"}
        missing = required - environments.keys()
        if missing:
            raise RuntimeError(f"Required existing environments are missing: {', '.join(sorted(missing))}")

        added_flags = add_flags(db, environments)
        all_flags = {(flag.environment.name, flag.key): flag for flag in db.scalars(select(Flag)).all()}
        added_memberships = add_memberships(db)
        added_rules = add_rules(db, all_flags, environments)
        added_versions = add_versions(db, added_flags)
        added_audits = add_audit_logs(db, all_flags, added_rules)
        db.commit()

        return {"flags": len(added_flags), "memberships": added_memberships, "rules": len(added_rules), "versions": added_versions, "audits": added_audits}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    result = seed()
    print("Demo seed complete:", ", ".join(f"{key} added={value}" for key, value in result.items()))
