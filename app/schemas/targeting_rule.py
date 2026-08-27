from pydantic import BaseModel
from typing import Any


class TargetingRuleCreate(BaseModel):
    flag_id: int
    priority: int = 1
    rule_type: str
    operator: str | None = None
    value: Any | None = None
    percentage: int | None = None
    enabled: bool = True
    is_active: bool = True
    

class TargetingRuleUpdate(BaseModel):
    flag_id: int
    priority: int
    rule_type: str
    operator: str | None = None
    value: Any | None = None
    percentage: int | None = None
    enabled: bool
    is_active: bool | None = None

