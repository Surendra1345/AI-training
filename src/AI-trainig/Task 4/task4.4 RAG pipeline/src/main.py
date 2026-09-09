from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from schemas import SearchRequest, SearchResponse
from search import semantic_search
from llm import generate_answer


app = FastAPI()


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    results = semantic_search(request.query, request.top_k)

    return SearchResponse(
        results=results
    )


@app.post("/search/llm", response_model=SearchResponse)
async def search_with_llm(request: SearchRequest):
    answer_data = generate_answer(
        request.query,
        request.top_k,
        request.coversation
    )
    return SearchResponse(
        answer=answer_data["answer"]
    )


DOCUMENT_DIR = Path(__file__).resolve().parent
@app.get("/src/{filename}")
def get_document(filename: str):
    file_path = DOCUMENT_DIR / filename

    print("Looking for:", file_path)
    print("Exists:", file_path.exists())

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return FileResponse(file_path)
