import fnmatch

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


class FakeRedis:
    """Minimal isolated cache for backend tests without a Redis service."""

    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value

    def scan_iter(self, match=None, count=None):
        yield from [key for key in list(self.values) if fnmatch.fnmatchcase(key, match)]

    def delete(self, *keys):
        deleted = 0
        for key in keys:
            if key in self.values:
                del self.values[key]
                deleted += 1
        return deleted


@pytest.fixture(autouse=True)
def isolated_evaluation_cache(monkeypatch):
    from app.services import evaluation_engine

    monkeypatch.setattr(evaluation_engine, "redis_client", FakeRedis())


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
