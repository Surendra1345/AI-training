from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.llm_schema import UserRequest, AssistantResponseSchema
from services.llm_service import UserRequestService, AssistantResponseService

router = APIRouter(prefix="/api/llm", tags=["LLM"])

@router.post("", response_model=AssistantResponseSchema)
async def llm_endpoint(request: UserRequest, db: Session = Depends(get_db)):
    # 1. Save user request
    user_request_service = UserRequestService(db)
    user_request_record = user_request_service.add_request(request)

    # 2. Call LLM API
    assistant_service = AssistantResponseService(db)
    llm_result = await assistant_service.call_llm_api(
        current_question=request.question, 
        request_id=user_request_record.id
    )

    # 3. Save and return the assistant response record
    response_record = assistant_service.add_response(llm_result)
    return response_record

@router.get("", response_model=list[AssistantResponseSchema])
def get_all_responses(db: Session = Depends(get_db)):
    assistant_service = AssistantResponseService(db)
    return assistant_service.repo.get_all_responses()
