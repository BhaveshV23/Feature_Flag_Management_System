import pytest
from pydantic import ValidationError

from app.api.flag_routes import create_flag, update_flag
from app.core.security import AuthenticatedUser
from app.models.flag import Flag
from app.schemas.feat_flag import FlagCreate, FlagUpdate
from app.services.evaluation_engine import evaluate_flag


def actor():
    return AuthenticatedUser(user_id=1, username="number-test")


@pytest.mark.parametrize("value, expected", [(42, 42), (0, 0), (-10, -10), (3.14, 3.14), (-2.75, -2.75), ("42", 42)])
def test_number_defaults_are_normalized(value, expected):
    request = FlagCreate(environment_id=1, key="number", name="Number", type="number", default_value=value, enabled=True, description="", owner_team="")
    assert request.default_value == expected
    assert isinstance(request.default_value, (int, float))


@pytest.mark.parametrize("value", ["abc", "12abc", "NaN", "Infinity", "-Infinity", float("nan"), float("inf"), float("-inf")])
def test_invalid_number_defaults_are_rejected(value):
    with pytest.raises(ValidationError):
        FlagCreate(environment_id=1, key="number", name="Number", type="number", default_value=value, enabled=True, description="", owner_team="")


def test_number_flag_crud_and_evaluation_preserve_numeric_value(db_session):
    environment = db_session.query(Flag).first().environment
    created = create_flag(
        FlagCreate(environment_id=environment.id, key="max_items", name="Maximum Items", type="number", default_value=25, enabled=True, description="", owner_team="platform"),
        db_session,
        actor(),
    )
    assert created.default_value == 25
    assert isinstance(created.default_value, int)

    result = evaluate_flag(db_session, "max_items", environment.name, {})
    assert result["value"] == 25
    assert isinstance(result["value"], int)

    updated = update_flag(
        created.id,
        FlagUpdate(key="max_items", type="number", default_value=-2.75, enabled=False, description="", owner_team="platform"),
        db_session,
        actor(),
    )
    assert updated.default_value == -2.75
    result = evaluate_flag(db_session, "max_items", environment.name, {})
    assert result["enabled"] is False
    assert result["value"] == -2.75
    assert isinstance(result["value"], float)
