from fastapi import APIRouter, Depends

from src.api.dependencies import get_rag_engine
from src.core.rag_engine import RAGEngine
from src.models.query import QueryRequest, QueryResponse

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    rag_engine: RAGEngine = Depends(get_rag_engine),
):
    print(request.__dict__)
    result = await rag_engine.query(request.question)
    print(result.__dict__)
    return QueryResponse(
        answer=result.answer,
        sources=[
            {"content": s.content, "source": s.metadata.get("source", ""), "score": s.score}
            for s in result.sources
        ],
    )
