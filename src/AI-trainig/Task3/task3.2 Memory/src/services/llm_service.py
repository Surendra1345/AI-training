import os
import logging
import httpx
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from repositories.repo import UserRequestRepository, AssistantResponseRepository
from schemas.llm_schema import UserRequest

load_dotenv()

# Load environment configuration
API_KEY = os.environ.get("Api-Key")
TEMPERATURE = float(os.environ.get("temperature", 0.7))
MODEL = os.environ.get("model")
TIMEOUT = float(os.environ.get("timeout", 60.0))

logging.basicConfig(level=logging.INFO)


class UserRequestService:
    def __init__(self, db: Session):
        self.repo = UserRequestRepository(db)

    def add_request(self, request: UserRequest):
        return self.repo.add_request(question=request.question)


class AssistantResponseService:
    def __init__(self, db: Session):
        self.repo = AssistantResponseRepository(db)
        self.user_repo = UserRequestRepository(db)

    async def call_llm_api(self, current_question: str, request_id: int) -> dict:
        # 1. Retrieve historical messages (ordered chronologically)
        history = self.user_repo.get_conversation_history(limit=5)

        # 2. Build the messages context array with System Prompt
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]

        # 3. Format previous interactions into context array
        for req in history:
            # Skip the current request if it's already stored in the DB to avoid duplicates
            if req.id == request_id:
                continue

            messages.append({"role": "user", "content": req.question})

            # Append past assistant responses linked to this request
            for res in req.responses:
                messages.append({"role": "assistant", "content": res.content})

        # 4. Append active prompt
        messages.append({"role": "user", "content": current_question})

        request_body = {
            "model": MODEL,
            "messages": messages,
            "temperature": TEMPERATURE,
            "max_tokens": 1000,
        }

        logging.info(f"Calling LLM with model: {MODEL} | Context messages: {len(messages)}")

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )

        if response.is_error:
            logging.error(f"Error calling LLM: {response.status_code} - {response.text}")
            raise Exception(f"LLM Provider Error: {response.status_code}")

        try:
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            logging.info("LLM response successfully received.")
            return {
                "request_id": request_id,
                "content": content,
            }
        except KeyError as e:
            logging.error(f"Error parsing LLM response: {e}")
            raise Exception(f"Error parsing LLM response: {e}")

    def add_response(self, response_data: dict):
        return self.repo.add_response(
            request_id=response_data["request_id"],
            content=response_data["content"],
        )