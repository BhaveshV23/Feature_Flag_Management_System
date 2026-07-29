from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text

from sqlalchemy.sql import func

from app.database.base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship

class Environment(Base):
    __tablename__ = "environments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
    
    flags: Mapped[list["Flag"]] = relationship(
        back_populates="environment",
        cascade="all, delete-orphan"
    )