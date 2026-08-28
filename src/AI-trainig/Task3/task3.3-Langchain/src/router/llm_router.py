from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.llm_schemas import UserRequest
from services.llm_service import AssistantResponseServiceRaw
from services.llm_service_langchain import AssistantResponseServiceLangChain

router = APIRouter(prefix="/llm", tags=["LLM Services"])

# ---------------------------------------------------------
# 1. RAW HTTP IMPLEMENTATION ENDPOINT
# ---------------------------------------------------------
@router.post("/raw/chat", status_code=status.HTTP_200_OK)
async def chat_raw(request: UserRequest, db: Session = Depends(get_db)):
    """Executes the prompt chain using native httpx and raw JSON formatting."""
    raw_service = AssistantResponseServiceRaw(db)
    
    # Save the incoming user question to DB
    user_request = raw_service.user_repo.add_request(question=request.question)
    
    # Call the raw LLM service
    response_data = await raw_service.call_llm_api(
        current_question=request.question, 
        request_id=user_request.id
    )
    
    # Store assistant response in DB
    raw_service.add_response(response_data)
    
    return response_data

@router.get("/raw/history", status_code=status.HTTP_200_OK)
def get_conversation_history(db: Session = Depends(get_db)):
    """Fetches the last 5 user requests and their corresponding assistant responses."""
    raw_service = AssistantResponseServiceRaw(db)
    history = raw_service.user_repo.get_conversation_history(limit=5)
    
    # Format the response to include both user questions and assistant responses
    formatted_history = []
    for req in history:
        formatted_entry = {
            "request_id": req.id,
            "question": req.question,
            "responses": [{"content": res.content} for res in req.responses]
        }
        formatted_history.append(formatted_entry)
    
    return {"history": formatted_history}



# ---------------------------------------------------------
# 2. LANGCHAIN LCEL IMPLEMENTATION ENDPOINT
# ---------------------------------------------------------
@router.post("/langchain/chat", status_code=status.HTTP_200_OK)
async def chat_langchain(request: UserRequest, db: Session = Depends(get_db)):
    """Executes the prompt chain using LangChain LCEL and Callback logging."""
    lc_service = AssistantResponseServiceLangChain(db)
    
    # Save the incoming user question to DB
    user_request = lc_service.user_repo.add_request(question=request.question)
    
    # Call the LangChain LCEL service (triggers OpenRouterTokenLogger)
    response_data = await lc_service.call_llm_api(
        current_question=request.question, 
        request_id=user_request.id
    )
    
    # Store assistant response in DB
    lc_service.add_response(response_data)
    
    return response_data
@router.get("/langchain/history", status_code=status.HTTP_200_OK)
def get_conversation_history_langchain(db: Session = Depends(get_db)):
    """Fetches the last 5 user requests and their corresponding assistant responses."""
    lc_service = AssistantResponseServiceLangChain(db)
    history = lc_service.user_repo.get_conversation_history(limit=5)
    
    # Format the response to include both user questions and assistant responses
    formatted_history = []
    for req in history:
        formatted_entry = {
            "request_id": req.id,
            "question": req.question,
            "responses": [{"content": res.content} for res in req.responses]
        }
        formatted_history.append(formatted_entry)
    
    return {"history": formatted_history}