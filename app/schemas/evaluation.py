from pydantic import BaseModel

class EvaluationRequest(BaseModel):
    flag_key: str
    environment_name: str
    user_context: dict | None = None