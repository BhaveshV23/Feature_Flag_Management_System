from pydantic import BaseModel, Field, field_validator


class EnvironmentSchema(BaseModel):
    name: str = Field(max_length=50)
    description: str | None = None
    is_active: bool

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Environment name must not be blank.")
        return value


class CreateEnvironment(EnvironmentSchema):
    pass
    
    
class UpdateEnvironment(EnvironmentSchema):
    pass
