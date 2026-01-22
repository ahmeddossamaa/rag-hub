from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class SourceInfo(BaseModel):
    content: str
    source: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
