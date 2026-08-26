from pydantic import BaseModel
import uuid

class UserRequest(BaseModel):
    role: str
    question: str

class AssistantResponse(BaseModel):
    request_id:uuid.UUID
    role: str
    content: str

