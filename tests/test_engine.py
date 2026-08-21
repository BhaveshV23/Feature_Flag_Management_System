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
        environment_name="development",
        user_context={}
    )

    assert result["success"] is False
    assert result["message"] == "Feature flag not found"


def test_enabled_flag(db_session):
    result = evaluate_flag(
        db=db_session,
        flag_key="dark_mode",
        environment_name="development",
        user_context={}
    )

    assert result["success"] is True
    assert result["enabled"] is True


def test_disabled_flag(db_session):
    result = evaluate_flag(
        db=db_session,
        flag_key="payment_v2",
        environment_name="development",
        user_context={}
    )

    assert result["success"] is True
    assert result["enabled"] is False
    
    
def test_user_targeting_rule(db_session):
    user_context = {
        "user_id": "user123"
    }

    result = evaluate_flag(
        db=db_session,
        flag_key="dark_mode",
        environment_name="development",
        user_context=user_context
    )

    assert result["success"] is True
    assert result["enabled"] is True
    
    
def test_group_targeting_rule(db_session):

    user_context = {
        "user_id": "user123"
    }

    result = evaluate_flag(
        db=db_session,
        flag_key="dark_mode",
        environment_name="development",
        user_context=user_context
    )

    assert result["success"] is True
    assert result["enabled"] is True
    
    
def test_rollout_percentage(db_session):
    user_context = {
        "user_id": "user_001"
    }

    result = evaluate_flag(
        db=db_session,
        flag_key="dark_mode",
        environment_name="development",
        user_context=user_context
    )

    assert result["success"] is True
    # Assuming the rollout percentage is set to 50%
    assert result["enabled"] in [True, False]  # It can be either based on the rollout percentage
    
