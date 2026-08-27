from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.flag import Flag
from app.models.targeting_rule import TargetingRule


def flag_to_dict(flag: Flag) -> dict:
    return {
        "id": flag.id,
        "environment_id": flag.environment_id,
        "key": flag.key,
        "name": flag.name,
        "description": flag.description,
        "enabled": flag.enabled,
        "type": flag.type,
        "default_value": flag.default_value,
        "owner_team": flag.owner_team,
    }


def targeting_rule_to_dict(rule: TargetingRule, environment_id: int) -> dict:
    return {
        "id": rule.id,
        "flag_id": rule.flag_id,
        "environment_id": environment_id,
        "priority": rule.priority,
        "rule_type": rule.rule_type,
        "operator": rule.operator,
        "value": rule.value,
        "percentage": rule.percentage,
        "enabled": rule.enabled,
        "is_active": rule.is_active,
    }


def create_audit_log(db: Session, *, flag_id: int | None, environment_id: int, actor: str, action: str, old_state: dict | None = None, new_state: dict | None = None) -> AuditLog:
    """Add an audit record without taking ownership of the transaction."""
    record = AuditLog(flag_id=flag_id, environment_id=environment_id, actor=actor, action=action, old_state=old_state, new_state=new_state)
    db.add(record)
    return record
