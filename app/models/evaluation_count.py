from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.base import Base


class EvaluationCount(Base):
    """Hourly evaluation aggregate awaiting persistence/reporting."""

    __tablename__ = "evaluation_counts"
    __table_args__ = (
        UniqueConstraint(
            "flag_id",
            "environment_id",
            "hour_start",
            name="uq_evaluation_count_flag_environment_hour",
        ),
        Index("ix_evaluation_counts_hour_start", "hour_start"),
        Index("ix_evaluation_counts_flag_environment", "flag_id", "environment_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    flag_id: Mapped[int] = mapped_column(ForeignKey("flags.id"), nullable=False, index=True)
    environment_id: Mapped[int] = mapped_column(ForeignKey("environments.id"), nullable=False, index=True)
    hour_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evaluation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
