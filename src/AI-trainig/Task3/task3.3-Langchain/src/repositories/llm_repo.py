from models.llm_model import UserRequest, AssistantResponse
from sqlalchemy.orm import Session, joinedload

class UserRequestRepository:

    def __init__(self, db: Session):
        self.db = db

    def add_request(self, question: str) -> UserRequest:
        db_request = UserRequest(question=question)
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        return db_request

    def get_conversation_history(self, limit: int = 10):
        # 1. Fetch the last 'limit' records (newest first) with their linked responses loaded
        records = (
            self.db.query(UserRequest)
            .options(joinedload(UserRequest.responses))
            .order_by(UserRequest.created_at.desc())
            .limit(limit)
            .all()
        )
        # 2. Reverse them so history reads chronologically (oldest to newest)
        return list(reversed(records))

    def get_all_requests(self):
        return self.db.query(UserRequest).all()


class AssistantResponseRepository:

    def __init__(self, db: Session):
        self.db = db

    def add_response(self, request_id: int, content: str) -> AssistantResponse:
        db_response = AssistantResponse(request_id=request_id, content=content)
        self.db.add(db_response)
        self.db.commit()
        self.db.refresh(db_response)
        return db_response

    def get_all_responses(self):
        return self.db.query(AssistantResponse).all()