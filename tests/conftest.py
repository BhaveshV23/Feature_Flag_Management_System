import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
# Importing app.models ensures every model class (Flag, Environment,
# FlagVersion, TargetingRule, AuditLog, UserGroupMembership) is registered
# on Base's metadata and all relationship() string references can resolve.
import app.models as models  # noqa: F401
from app.models.environment import Environment
from app.models.flag import Flag


@pytest.fixture()
def db_session():
    # In-memory SQLite DB, isolated per test. StaticPool + check_same_thread=False
    # keeps a single connection alive for the lifetime of the engine, which is
    # required for SQLite ":memory:" databases to work with SQLAlchemy sessions.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = TestingSessionLocal()

    # --- Seed data expected by test_engine.py ---
    dev_env = Environment(name="development", description="Dev environment")
    session.add(dev_env)
    session.flush()  # populate dev_env.id without committing

    dark_mode = Flag(
        environment_id=dev_env.id,
        key="dark_mode",
        name="Dark Mode",
        description="Enables dark mode UI",
        enabled=True,
        type="boolean",
        default_value="true",
        owner_team="frontend",
    )

    payment_v2 = Flag(
        environment_id=dev_env.id,
        key="payment_v2",
        name="Payment V2",
        description="New payment flow",
        enabled=False,
        type="boolean",
        default_value="false",
        owner_team="payments",
    )

    session.add_all([dark_mode, payment_v2])
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()