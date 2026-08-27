from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.audit_log import AuditLog


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    flag_id: int | None
    environment_id: int
    actor: str
    action: str
    created_at: datetime
    old_state: dict | None
    new_state: dict | None


router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db),
    flag_id: int | None = Query(default=None),
    environment_id: int | None = Query(default=None),
    actor: str | None = Query(default=None),
    action: str | None = Query(default=None),
):
    query = db.query(AuditLog)
    if flag_id is not None:
        query = query.filter(AuditLog.flag_id == flag_id)
    if environment_id is not None:
        query = query.filter(AuditLog.environment_id == environment_id)
    if actor:
        query = query.filter(AuditLog.actor == actor)
    if action:
        query = query.filter(AuditLog.action == action)
    return query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).all()
