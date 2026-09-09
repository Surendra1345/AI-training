from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    top_k: int 
    conversation:list[chatMessage] | None = None

class SearchResult(BaseModel):
    content: str
    similarity: float
    source: str | None
    page: int | None

class Citation(BaseModel):
    document: str
    page: int
    url: str

class chatMessage(BaseModel):
    role: str
    content: str

class SearchResponse(BaseModel):
    answer: str | None = None
    # results: list[SearchResult]
    citations: list[Citation] | None = None