from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)

class Flag(Base):
    __tablename__ = "flags"
    
    __table_args__ = (
        UniqueConstraint(
            "environment_id",
            "key",
            name="uq_environment_flag_key",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    environment_id: Mapped[int] = mapped_column(
        ForeignKey("environments.id"),
        nullable=False,
        index=True
    )

    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    # JSON preserves legacy strings while allowing native numeric defaults.
    default_value: Mapped[object | None] = mapped_column(JSON, nullable=True)
    owner_team: Mapped[str | None]

    environment = relationship("Environment", back_populates="flags")
    
    versions: Mapped[list["FlagVersion"]] = relationship(
        back_populates="flag",
        cascade="all, delete-orphan",
    )
    
    targeting_rules: Mapped[list["TargetingRule"]] = relationship(
        back_populates="flag",
        cascade="all, delete-orphan",
    )
