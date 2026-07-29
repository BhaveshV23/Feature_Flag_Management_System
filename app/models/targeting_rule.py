from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class TargetingRule(Base):
    __tablename__ = "targeting_rules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    flag_id: Mapped[int] = mapped_column(
        ForeignKey("flags.id"),
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    rule_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    operator: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    value: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    percentage: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    flag = relationship(
        "Flag",
        back_populates="targeting_rules",
    )