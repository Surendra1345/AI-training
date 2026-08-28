from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Pydantic schema for incoming request payload
class UserRequest(BaseModel):
    question: str


# Pydantic schema for output response
class AssistantResponse(BaseModel):
    id: int
    request_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)