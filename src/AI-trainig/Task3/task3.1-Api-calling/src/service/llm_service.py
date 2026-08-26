import os
import uuid
import httpx
import logging
from fastapi import HTTPException
from dotenv import load_dotenv
from schemas.schema import UserRequest, AssistantResponse

load_dotenv()

logging.basicConfig(level=logging.INFO)

api_key = os.getenv("Api-Key") 
model = os.getenv("MODEL")
temperature = float(os.getenv("TEMPERATURE", 0.5))
timeout = float(os.getenv("TIMEOUT", 30))

if not api_key:
    raise ValueError("Api-Key is not set in environment variables")

async def call_llm_api(request: UserRequest,request_id:uuid.UUID) -> AssistantResponse:
    request_body = {
        "model": model,
        "messages": [
            {
                "role": request.role,
                "content": request.question
            }
        ],
        "temperature": temperature,
        "max_tokens": 1000
    }

    logging.info(f"Calling LLM with model: {model}")

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=request_body,
        )

    if response.is_error:
        logging.error(f"Error calling LLM: {response.status_code}")
        raise HTTPException(status_code=response.status_code, detail="LLM Provider Error")

    try:
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        logging.info("LLM response.")
        return AssistantResponse(
            request_id=request_id,
            role="assistant",
            content=content
        )
    except (KeyError, IndexError) as e:
        logging.error(f"Failed to parse OpenRouter response payload: {str(e)}")
        raise HTTPException(status_code=500, detail="Malformed payload received from LLM provider")

async def stream_llm_api(request: UserRequest,request_id:uuid.UUID):
    request_body = {
        "model": model,
        "messages": [
            {
                "role": request.role,
                "content": request.question
            }
        ],
        "temperature": temperature,
        "max_tokens": 1000,
        "stream": True
    }

    logging.info(f"Calling LLM with model with streaming: {model}")

    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=request_body
        ) as response:
            if response.is_error:
                error_text = await response.aread()
                logging.error(f"Streaming error encounter: {response.status_code}")
                yield f"data: Error: {error_text.decode()}\n\n"
                return

            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    yield f"{line}\n\n"
            
            logging.info("Streaming response completed successfully.")