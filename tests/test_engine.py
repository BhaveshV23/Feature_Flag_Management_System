import pytest

from app.services.evaluation_engine import evaluate_flag


def test_environment_not_found(db_session):
    result = evaluate_flag(
        db=db_session,
        flag_key="dark_mode",
        environment_name="invalid"
    )

    assert result["success"] is False
    assert result["message"] == "Environment not found"


def test_flag_not_found(db_session):
    result = evaluate_flag(
        db=db_session,
        flag_key="invalid_flag",
        environment_name="development"
    )

    assert result["success"] is False
    assert result["message"] == "Feature flag not found"


def test_enabled_flag(db_session):
    result = evaluate_flag(
        db=db_session,
        flag_key="dark_mode",
        environment_name="development"
    )

    assert result["success"] is True
    assert result["enabled"] is True


def test_disabled_flag(db_session):
    result = evaluate_flag(
        db=db_session,
        flag_key="payment_v2",
        environment_name="development"
    )

    assert result["success"] is True
    assert result["enabled"] is False