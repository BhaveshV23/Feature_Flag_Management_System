from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.evaluation_count import EvaluationCount
from app.schemas.evaluation_analytics import EvaluationAnalyticsResponse


router = APIRouter(dependencies=[Depends(get_current_user)])


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@router.get("/analytics/evaluations", response_model=list[EvaluationAnalyticsResponse])
def get_evaluation_analytics(
    db: Session = Depends(get_db),
    flag_id: int | None = Query(default=None),
    environment_id: int | None = Query(default=None),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
):
    """Return hourly evaluation counts, defaulting to the most recent 30 days."""

    now = datetime.now(timezone.utc)
    start_utc = _utc(start) if start is not None else None
    end_utc = _utc(end) if end is not None else None

    if start_utc is not None and end_utc is not None and start_utc >= end_utc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="start must be earlier than end.")

    if start_utc is None:
        start_utc = end_utc - timedelta(days=30) if end_utc is not None else now - timedelta(days=30)
    if end_utc is None:
        end_utc = now

    query = db.query(EvaluationCount)
    if flag_id is not None:
        query = query.filter(EvaluationCount.flag_id == flag_id)
    if environment_id is not None:
        query = query.filter(EvaluationCount.environment_id == environment_id)
    query = query.filter(EvaluationCount.hour_start >= start_utc, EvaluationCount.hour_start < end_utc)
    rows = query.order_by(EvaluationCount.hour_start.asc(), EvaluationCount.environment_id.asc(), EvaluationCount.flag_id.asc()).all()

    return [
        EvaluationAnalyticsResponse(
            flag_id=row.flag_id,
            environment_id=row.environment_id,
            hour_start=_utc(row.hour_start),
            evaluation_count=row.evaluation_count,
        )
        for row in rows
    ]
