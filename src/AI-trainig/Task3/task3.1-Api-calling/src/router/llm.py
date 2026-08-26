from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import uuid
from schemas.schema import UserRequest, AssistantResponse
from service.llm_service import call_llm_api, stream_llm_api


router = APIRouter(
    prefix="/api",
    tags=["LLM"]
)


@router.post(
    "/llm",
    response_model=AssistantResponse
)
async def llm_endpoint(
    request: UserRequest
) -> AssistantResponse:
    request_id = uuid.uuid4()
    response = await call_llm_api(request, request_id)
    return response


@router.post("/stream")
async def stream_endpoint(request: UserRequest):
    request_id = uuid.uuid4()
    return StreamingResponse(
        stream_llm_api(request, request_id),
        media_type="text/event-stream"
    )