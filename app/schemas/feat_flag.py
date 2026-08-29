from decimal import Decimal, InvalidOperation
from typing import Any, Literal

from pydantic import BaseModel, model_validator

FlagType = Literal["boolean", "string", "number"]


def _normalize_default(flag_type: str, value: Any) -> Any:
    if flag_type != "number":
        return value
    if isinstance(value, bool) or value is None:
        raise ValueError("Number flag default_value must be a finite number.")
    try:
        number = Decimal(value.strip()) if isinstance(value, str) else Decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Number flag default_value must be a finite number.") from None
    if not number.is_finite():
        raise ValueError("Number flag default_value must be a finite number.")
    return int(number) if number == number.to_integral_value() else float(number)


class FlagCreate(BaseModel):
    environment_id: int
    key: str
    name: str
    type: FlagType
    default_value: Any
    enabled: bool
    description: str
    owner_team: str

    @model_validator(mode="after")
    def validate_default_value(self):
        self.default_value = _normalize_default(self.type, self.default_value)
        return self


class FlagUpdate(BaseModel):
    key: str
    type: FlagType
    default_value: Any
    enabled: bool
    description: str
    owner_team: str

    @model_validator(mode="after")
    def validate_default_value(self):
        self.default_value = _normalize_default(self.type, self.default_value)
        return self
