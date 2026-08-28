from fastapi import FastAPI
from router.llm_router import router

app = FastAPI(title="LLM API Service")

app.include_router(router)
