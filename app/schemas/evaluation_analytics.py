from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EvaluationAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    flag_id: int
    environment_id: int
    hour_start: datetime
    evaluation_count: int
