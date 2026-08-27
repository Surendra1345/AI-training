from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserRequest(BaseModel):
    question: str

class AssistantResponseSchema(BaseModel):
    id: int
    request_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)