from pydantic import BaseModel

class CreateEnvironment(BaseModel):
    name: str
    description: str | None = None
    is_active: bool
    
    
class UpdateEnvironment(BaseModel):
    name: str
    description: str | None = None
    is_active: bool