import os
import logging
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from repositories.llm_repo import UserRequestRepository, AssistantResponseRepository
from services.callback import OpenRouterTokenLogger

load_dotenv()

api_key = os.environ.get("Api-Key")
model_name = os.environ.get("model")
temperature = float(os.environ.get("temperature", 0.9))

class AssistantResponseServiceLangChain:
    def __init__(self, db: Session):
        self.repo = AssistantResponseRepository(db)
        self.user_repo = UserRequestRepository(db)
        
        # 1. Chat Model Provider Abstraction
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature,
        )

        # 2. Prompt Template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{current_question}"),
        ])

        # 3. LCEL Chain Construction
        self.chain = self.prompt | self.llm | StrOutputParser()

    async def call_llm_api(self, current_question: str, request_id: int) -> dict:
        db_history = self.user_repo.get_conversation_history(limit=5)
        
        chat_history = []
        for req in db_history:
            if req.id == request_id:
                continue
            chat_history.append(HumanMessage(content=req.question))
            for res in req.responses:
                chat_history.append(AIMessage(content=res.content))

        token_logger = OpenRouterTokenLogger()

        try:
            # Invoking LCEL chain with Callback Config
            content = await self.chain.ainvoke(
                {
                    "chat_history": chat_history,
                    "current_question": current_question
                },
                config={"callbacks": [token_logger]}
            )
            return {"request_id": request_id, "role": "assistant", "content": content}

        except Exception as e:
            logging.error(f"Error executing LangChain execution pipeline: {str(e)}")
            raise Exception("LLM Provider Error")

    def add_response(self, response_data: dict):
        return self.repo.add_response(
            request_id=response_data["request_id"],
            content=response_data["content"],
        )