import os
import logging
import httpx
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("Api-Key")
temperature = float(os.environ.get("temperature", 0.9))
timeout = float(os.environ.get("timeout", 60.0))
model = os.environ.get("model")

class AssistantResponseServiceRaw:
    def __init__(self, db: Session):
        from repositories.llm_repo import UserRequestRepository, AssistantResponseRepository
        self.repo = AssistantResponseRepository(db)
        self.user_repo = UserRequestRepository(db)

    async def call_llm_api(self, current_question: str, request_id: int) -> dict:
        history = self.user_repo.get_conversation_history(limit=5)
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        for req in history:
            if req.id == request_id:
                continue
            messages.append({"role": "user", "content": req.question})
            for res in req.responses:
                messages.append({"role": "assistant", "content": res.content})
        messages.append({"role": "user", "content": current_question})

        request_body = {"model": model, "messages": messages}
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=request_body,
            )

            response_data = response.json()

            # Catch non-200 responses or payloads containing errors
            if response.is_error or "error" in response_data:
                logging.error(f"OpenRouter API Error: {response_data}")
                raise Exception(f"LLM Provider Error: {response_data.get('error', {}).get('message', 'Unknown Error')}")

            try:
                content = response_data["choices"][0]["message"]["content"]
                return {"request_id": request_id, "role": "assistant", "content": content}
            except (KeyError, IndexError) as e:
                logging.error(f"Malformed payload received: {response_data}")
                raise Exception("Malformed payload received from LLM provider")

    def add_response(self, response_data: dict):
        return self.repo.add_response(
            request_id=response_data["request_id"],
            content=response_data["content"],
        )