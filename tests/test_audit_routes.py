from datetime import datetime, timezone

from test_auth import client

from app.api.audit_routes import get_audit_logs
from app.models.audit_log import AuditLog


def test_audit_logs_return_newest_first_and_preserve_snapshots(db_session):
    db_session.add_all([
        AuditLog(environment_id=1, actor="older", action="CREATE", old_state=None, new_state={"key": "old"}, created_at=datetime(2024, 1, 1, tzinfo=timezone.utc)),
        AuditLog(environment_id=1, actor="newer", action="UPDATE", old_state={"enabled": False}, new_state={"enabled": True}, created_at=datetime(2024, 1, 2, tzinfo=timezone.utc)),
    ])
    db_session.commit()
    records = get_audit_logs(db_session, None, None, None, None)
    assert [record.actor for record in records] == ["newer", "older"]
    assert records[0].old_state == {"enabled": False}
    assert records[0].new_state == {"enabled": True}
    assert records[0].environment_id == 1


def test_audit_logs_filter_by_action_and_environment(db_session):
    db_session.add_all([
        AuditLog(environment_id=1, actor="admin", action="CREATE"),
        AuditLog(environment_id=1, actor="admin", action="TARGETING_RULE_UPDATE"),
    ])
    db_session.commit()
    assert len(get_audit_logs(db_session, None, None, None, "CREATE")) == 1
    assert len(get_audit_logs(db_session, None, 1, "admin", None)) == 2


def test_audit_route_requires_authentication(client):
    response = client("GET", "/api/audit-logs")
    assert response["status"] == 401
