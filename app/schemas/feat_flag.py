from pydantic import BaseModel

class FlagCreate(BaseModel):
    environment_id: int
    key: str
    name: str
    type: str
    default_value: str
    enabled: bool
    description: str
    owner_team: str
    

class FlagUpdate(BaseModel):
    key: str
    type: str
    default_value: str
    enabled: bool
    description: str
    owner_team: str